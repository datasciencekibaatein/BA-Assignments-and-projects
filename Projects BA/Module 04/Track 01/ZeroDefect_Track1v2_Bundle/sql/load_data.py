"""
Load Olist data into a SQLite database following the schema in schema.sql.
Run from the project root: python sql/load_data.py
"""
import sqlite3
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
SQL_DIR  = ROOT / "sql"
DB_PATH  = ROOT / "outputs" / "olist_audit.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)

# Run schema
schema_sql = (SQL_DIR / "schema.sql").read_text()
# Execute statement by statement (some SQLite drivers don't like multi-statement)
for stmt in schema_sql.split(';'):
    stmt = stmt.strip()
    if stmt:
        conn.executescript(stmt + ';')
print("Schema created.")

# Load each table
def load(name, csv_name, col_map=None, parse_dates=None):
    df = pd.read_csv(DATA_DIR / csv_name)
    if col_map:
        df = df.rename(columns=col_map)
    if parse_dates:
        for c in parse_dates:
            df[c] = pd.to_datetime(df[c], errors='coerce')
    df.to_sql(name, conn, if_exists="append", index=False)
    print(f"  Loaded {name}: {len(df):,} rows")

print("Loading tables...")
load("customers", "olist_customers_dataset.csv",
     col_map={"customer_zip_code_prefix":"customer_zip_prefix"})
load("sellers", "olist_sellers_dataset.csv",
     col_map={"seller_zip_code_prefix":"seller_zip_prefix"})
load("product_categories", "product_category_name_translation.csv",
     col_map={"product_category_name":"category_pt", "product_category_name_english":"category_en"})

prods = pd.read_csv(DATA_DIR / "olist_products_dataset.csv")
prods = prods.rename(columns={
    "product_category_name":"category_pt",
    "product_name_lenght":"name_length",
    "product_description_lenght":"desc_length",
    "product_photos_qty":"photos_qty",
    "product_weight_g":"weight_g",
    "product_length_cm":"length_cm",
    "product_height_cm":"height_cm",
    "product_width_cm":"width_cm",
})
prods.to_sql("products", conn, if_exists="append", index=False)
print(f"  Loaded products: {len(prods):,} rows")

orders = pd.read_csv(DATA_DIR / "olist_orders_dataset.csv")
orders = orders.rename(columns={
    "order_purchase_timestamp":"purchase_ts",
    "order_approved_at":"approved_ts",
    "order_delivered_carrier_date":"carrier_pickup_ts",
    "order_delivered_customer_date":"customer_delivered_ts",
    "order_estimated_delivery_date":"estimated_delivery_ts",
})
for c in ["purchase_ts","approved_ts","carrier_pickup_ts","customer_delivered_ts","estimated_delivery_ts"]:
    orders[c] = pd.to_datetime(orders[c], errors='coerce')
orders.to_sql("orders", conn, if_exists="append", index=False)
print(f"  Loaded orders: {len(orders):,} rows")

items = pd.read_csv(DATA_DIR / "olist_order_items_dataset.csv")
items = items.rename(columns={
    "order_item_id":"item_seq",
    "shipping_limit_date":"shipping_limit_ts",
})
items["shipping_limit_ts"] = pd.to_datetime(items["shipping_limit_ts"], errors='coerce')
items.to_sql("order_items", conn, if_exists="append", index=False)
print(f"  Loaded order_items: {len(items):,} rows")

pays = pd.read_csv(DATA_DIR / "olist_order_payments_dataset.csv")
pays = pays.rename(columns={
    "payment_sequential":"payment_seq",
})
pays.to_sql("order_payments", conn, if_exists="append", index=False)
print(f"  Loaded order_payments: {len(pays):,} rows")

revs = pd.read_csv(DATA_DIR / "olist_order_reviews_dataset.csv")
revs = revs.rename(columns={
    "review_creation_date":"review_creation_ts",
    "review_answer_timestamp":"review_answer_ts",
})
for c in ["review_creation_ts","review_answer_ts"]:
    revs[c] = pd.to_datetime(revs[c], errors='coerce')
# Drop the long text columns we don't need (review_comment_title, review_comment_message)
keep = ["review_id","order_id","review_score","review_creation_ts","review_answer_ts"]
revs = revs[keep]
# Drop duplicates on (review_id, order_id)
revs = revs.drop_duplicates(subset=["review_id","order_id"])
revs.to_sql("order_reviews", conn, if_exists="append", index=False)
print(f"  Loaded order_reviews: {len(revs):,} rows")

# Verify views work
print("\nValidating views...")
for view in ["v_order_lead_times","v_state_performance","v_seller_performance",
             "v_category_performance","v_daily_order_volume","v_review_vs_delay"]:
    n = conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]
    print(f"  {view:<28} {n:>8,} rows")

conn.commit()
conn.close()
print(f"\nDB saved to {DB_PATH} ({DB_PATH.stat().st_size/1024/1024:.1f} MB)")
