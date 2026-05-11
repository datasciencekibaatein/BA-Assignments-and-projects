
import pandas as pd
import sqlite3
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA = BASE_DIR / "../../dataset/DataCoSupplyChainDataset.csv"
DB   = BASE_DIR / "../../dataset/dataco.db"
SCHEMA_SQL = (BASE_DIR / "schema.sql").read_text()


# SQLite-compatible version (drop CHECK constraints with CASE, drop SERIAL, etc.)
def to_sqlite_ddl(pg_ddl):
    s = pg_ddl
    s = re.sub(r"BIGSERIAL", "INTEGER", s, flags=re.IGNORECASE)
    s = re.sub(r"SERIAL",    "INTEGER", s, flags=re.IGNORECASE)
    s = re.sub(r"BIGINT",    "INTEGER", s, flags=re.IGNORECASE)
    s = re.sub(r"DECIMAL\([^)]+\)", "REAL", s, flags=re.IGNORECASE)
    s = re.sub(r"BOOLEAN",   "INTEGER", s, flags=re.IGNORECASE)
    s = re.sub(r"TIMESTAMP", "TEXT",    s, flags=re.IGNORECASE)
    s = re.sub(r"VARCHAR\([^)]+\)", "TEXT", s, flags=re.IGNORECASE)
    s = re.sub(r"\bTEXT\b",  "TEXT",    s)
    s = re.sub(r"DROP TABLE.*CASCADE;", lambda m: m.group().replace(" CASCADE",""), s)
    s = re.sub(r"::numeric", "", s)
    # SQLite: no CREATE OR REPLACE VIEW. Replace with DROP+CREATE
    s = re.sub(r"CREATE OR REPLACE VIEW (\w+) AS",
                r"DROP VIEW IF EXISTS \1;\nCREATE VIEW \1 AS", s, flags=re.IGNORECASE)
    # SQLite: LEAST(...) -> MIN(...)
    s = re.sub(r"\bLEAST\b", "MIN", s)
    return s

ddl = to_sqlite_ddl(SCHEMA_SQL)

# Read source CSV
print("Loading CSV...")
dc = pd.read_csv(DATA, encoding="latin-1", low_memory=False)
print(f"  {len(dc):,} rows, {len(dc.columns)} cols")

# Connect & create schema
if DB.exists():
    DB.unlink()
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.executescript(ddl)
conn.commit()

# ==================== Populate dimension tables ====================
# markets
markets = sorted(dc["Market"].unique())
for m in markets:
    cur.execute("INSERT INTO markets(market_name) VALUES (?)", (m,))
conn.commit()
mkt_id = {m: i+1 for i,m in enumerate(markets)}

# regions
region_to_market = dc[["Order Region","Market"]].drop_duplicates()
for _, r in region_to_market.iterrows():
    cur.execute("INSERT INTO regions(region_name, market_id) VALUES (?, ?)",
                  (r["Order Region"], mkt_id[r["Market"]]))
conn.commit()
reg_id = {row[1]: row[0] for row in cur.execute("SELECT region_id, region_name FROM regions").fetchall()}

# shipping_modes (with explicit SLA values from data)
mode_slas = {
    "Standard Class": 4.0,
    "Second Class":   2.0,
    "First Class":    1.0,
    "Same Day":       0.0,
}
mode_descs = {
    "Standard Class": "4-day economy ground service - the operational baseline",
    "Second Class":   "2-day expedited - typically air-supported",
    "First Class":    "1-day priority - tightest SLA, highest failure rate",
    "Same Day":       "Same-day local courier - 0-day SLA, often delivered next morning",
}
for m, sla in mode_slas.items():
    cur.execute("INSERT INTO shipping_modes(mode_name, sla_scheduled_days, description) VALUES (?,?,?)",
                  (m, sla, mode_descs[m]))
conn.commit()
mode_id = {row[1]: row[0] for row in cur.execute("SELECT mode_id, mode_name FROM shipping_modes").fetchall()}

# departments
depts = dc[["Department Id","Department Name"]].drop_duplicates().sort_values("Department Id")
for _, d in depts.iterrows():
    cur.execute("INSERT INTO departments(department_id, department_name) VALUES (?, ?)",
                  (int(d["Department Id"]), d["Department Name"]))
conn.commit()

# categories
cats = dc[["Category Id","Category Name","Department Id"]].drop_duplicates().sort_values("Category Id")
for _, c in cats.iterrows():
    cur.execute("INSERT INTO categories(category_id, category_name, department_id) VALUES (?, ?, ?)",
                  (int(c["Category Id"]), c["Category Name"], int(c["Department Id"])))
conn.commit()

# products
prods = dc[["Product Card Id","Product Name","Category Id","Product Price"]].drop_duplicates().sort_values("Product Card Id")
for _, p in prods.iterrows():
    cur.execute("INSERT INTO products(product_id, product_name, category_id, list_price) VALUES (?,?,?,?)",
                  (int(p["Product Card Id"]), p["Product Name"], int(p["Category Id"]), float(p["Product Price"])))
conn.commit()

# customers
cust_cols = ["Customer Id","Customer Fname","Customer Lname","Customer Segment",
             "Customer City","Customer State","Customer Country","Customer Zipcode"]
custs = dc[cust_cols].drop_duplicates(subset=["Customer Id"]).sort_values("Customer Id")
custs.to_sql("_tmp_customers", conn, if_exists="replace", index=False)
cur.execute("""
INSERT INTO customers(customer_id, customer_fname, customer_lname, customer_segment,
                      customer_city, customer_state, customer_country, customer_zipcode)
SELECT "Customer Id","Customer Fname","Customer Lname","Customer Segment",
       "Customer City","Customer State","Customer Country","Customer Zipcode"
FROM _tmp_customers
""")
cur.execute("DROP TABLE _tmp_customers")
conn.commit()

# routes (origin_state, dest_state, dest_country, region_id)
routes_src = dc[["Customer State","Order State","Order Country","Order Region"]].drop_duplicates()
print(f"  Routes (unique O-D-Country-Region tuples): {len(routes_src):,}")
for _, r in routes_src.iterrows():
    cur.execute("""INSERT INTO routes(origin_state, destination_state, destination_country, region_id)
                   VALUES (?,?,?,?)""",
                  (r["Customer State"], r["Order State"], r["Order Country"], reg_id[r["Order Region"]]))
conn.commit()

# Get a route lookup
route_lookup_df = pd.read_sql("""
SELECT route_id, origin_state, destination_state, destination_country FROM routes
""", conn)
route_key = route_lookup_df.set_index(["origin_state","destination_state","destination_country"])["route_id"].to_dict()

# ==================== Populate fact tables ====================
# orders: aggregate by Order Id (drop dup lines) - take first row's order-level fields
order_cols = [
    "Order Id","Customer Id","Customer State","Order State","Order Country",
    "Shipping Mode","order date (DateOrders)","shipping date (DateOrders)",
    "Days for shipping (real)","Days for shipment (scheduled)",
    "Delivery Status","Late_delivery_risk","Order Status","Order Profit Per Order",
]
orders_df = dc[order_cols].drop_duplicates(subset=["Order Id"])
print(f"  Orders (unique): {len(orders_df):,}")

orders_to_insert = []
for _, o in orders_df.iterrows():
    rk = (o["Customer State"], o["Order State"], o["Order Country"])
    rid = route_key.get(rk)
    if rid is None:
        continue
    # Parse to ISO format (avoids SQLite's lexicographic string comparison breaking CHECK constraint)
    od = pd.to_datetime(o["order date (DateOrders)"]).isoformat(sep=" ")
    sd = pd.to_datetime(o["shipping date (DateOrders)"]).isoformat(sep=" ")
    orders_to_insert.append((
        int(o["Order Id"]),
        int(o["Customer Id"]),
        rid,
        mode_id[o["Shipping Mode"]],
        od,
        sd,
        float(o["Days for shipping (real)"]),
        float(o["Days for shipment (scheduled)"]),
        o["Delivery Status"],
        int(o["Late_delivery_risk"]),
        o["Order Status"],
        float(o["Order Profit Per Order"]) if pd.notna(o["Order Profit Per Order"]) else None,
    ))

cur.executemany("""
INSERT INTO orders(order_id, customer_id, route_id, mode_id, order_date, shipping_date,
                    days_shipping_real, days_shipping_sched, delivery_status,
                    late_delivery_risk, order_status, order_profit)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
""", orders_to_insert)
conn.commit()
print(f"  Inserted {len(orders_to_insert):,} orders")

# order_items
items_df = dc[["Order Id","Product Card Id","Order Item Quantity","Order Item Product Price",
                "Order Item Discount","Order Item Discount Rate","Order Item Total","Order Item Profit Ratio"]].copy()
items_df.columns = ["order_id","product_id","quantity","unit_price","discount",
                      "discount_rate","item_total","profit_ratio"]
items_df.to_sql("order_items_stg", conn, if_exists="replace", index=False)
cur.execute("""
INSERT INTO order_items(order_id, product_id, quantity, unit_price, discount,
                         discount_rate, item_total, profit_ratio)
SELECT order_id, product_id, quantity, unit_price, discount,
       discount_rate, item_total, profit_ratio
FROM order_items_stg
""")
cur.execute("DROP TABLE order_items_stg")
conn.commit()
n_items = cur.execute("SELECT COUNT(*) FROM order_items").fetchone()[0]
print(f"  Inserted {n_items:,} order_items")

# Quick sanity-check: row counts
print("\n=== Row counts ===")
for t in ["markets","regions","shipping_modes","departments","categories","products",
           "customers","routes","orders","order_items"]:
    n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t:<20} {n:>10,}")

conn.close()
print(f"\nDB saved to {DB} ({DB.stat().st_size/1024/1024:.1f} MB)")
