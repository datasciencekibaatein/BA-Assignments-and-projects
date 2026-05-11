"""
Loads DataCo CSV into SQLite using the schema in schema.sql.
Auto-resolves project root by folder name OR by sibling dirs.
"""
import os
import sys
import sqlite3
import pandas as pd
from pathlib import Path

def find_project_root():
    cwd = Path(__file__).resolve().parent
    # Look for the lean_shield folder up the tree, or fall back to parent
    for p in [cwd, cwd.parent, cwd.parent.parent, cwd.parent.parent.parent]:
        if (p / 'sql').exists() and (p / 'sql' / 'schema.sql').exists():
            return p
    return cwd.parent

ROOT = find_project_root()
DATA = ROOT / 'data' / 'DataCoSupplyChainDataset.csv'
SCHEMA = ROOT / 'sql' / 'schema.sql'
OUTPUTS = ROOT / 'outputs'
OUTPUTS.mkdir(exist_ok=True)
DB = OUTPUTS / 'leanshield.db'

print(f"Project root: {ROOT}")
print(f"Data:    {DATA}  exists={DATA.exists()}")
print(f"Schema:  {SCHEMA}")
print(f"DB:      {DB}")

# Load data
print("\nReading DataCo CSV...")
df = pd.read_csv(DATA, encoding='latin-1')
print(f"  Loaded {len(df):,} rows x {len(df.columns)} columns")

# Connect to SQLite, drop & rebuild
if DB.exists():
    DB.unlink()
conn = sqlite3.connect(DB)
cur = conn.cursor()

# Apply schema
print("\nApplying schema...")
schema_sql = SCHEMA.read_text()
cur.executescript(schema_sql)
conn.commit()

# dim_product
print("\nLoading dim_product...")
dim_p = (df[['Product Card Id', 'Product Name', 'Category Id', 'Category Name',
             'Department Id', 'Department Name', 'Product Price']]
         .drop_duplicates(subset=['Product Card Id']))
dim_p.columns = ['product_card_id', 'product_name', 'category_id', 'category_name',
                 'department_id', 'department_name', 'product_price']
dim_p.to_sql('dim_product', conn, if_exists='append', index=False)
print(f"  dim_product: {len(dim_p):,} rows")

# dim_customer
print("Loading dim_customer...")
dim_c = (df[['Customer Id', 'Customer Segment', 'Customer Country',
             'Customer State', 'Customer City']]
         .drop_duplicates(subset=['Customer Id']))
dim_c.columns = ['customer_id', 'customer_segment', 'customer_country',
                 'customer_state', 'customer_city']
dim_c.to_sql('dim_customer', conn, if_exists='append', index=False)
print(f"  dim_customer: {len(dim_c):,} rows")

# dim_warehouse (Market = warehouse in our framing)
print("Loading dim_warehouse...")
dim_w = pd.DataFrame({
    'market_name': df['Market'].unique(),
    'region':      df['Market'].unique(),
})
dim_w.to_sql('dim_warehouse', conn, if_exists='append', index=False)
print(f"  dim_warehouse: {len(dim_w)} rows")

# fact_orders
print("Loading fact_orders...")
fact = df[['Order Item Id', 'Order Id', 'order date (DateOrders)',
           'shipping date (DateOrders)', 'Customer Id', 'Product Card Id',
           'Market', 'Order Region', 'Order Country',
           'Shipping Mode', 'Order Status', 'Delivery Status',
           'Days for shipping (real)', 'Days for shipment (scheduled)',
           'Late_delivery_risk', 'Order Item Quantity', 'Order Item Total',
           'Order Profit Per Order', 'Sales', 'Type']].copy()
fact.columns = ['order_item_id', 'order_id', 'order_date', 'shipping_date',
                'customer_id', 'product_card_id', 'market', 'order_region',
                'order_country', 'shipping_mode', 'order_status', 'delivery_status',
                'days_shipping_real', 'days_shipment_scheduled', 'late_delivery_risk',
                'order_item_quantity', 'order_item_total', 'order_profit_per_order',
                'sales', 'type']
fact['order_date']    = pd.to_datetime(fact['order_date']).dt.strftime('%Y-%m-%d')
fact['shipping_date'] = pd.to_datetime(fact['shipping_date']).dt.strftime('%Y-%m-%d')
fact.to_sql('fact_orders', conn, if_exists='append', index=False)
print(f"  fact_orders: {len(fact):,} rows")

# Verify
print("\n=== Verification ===")
for tbl in ['dim_product', 'dim_customer', 'dim_warehouse', 'fact_orders']:
    n = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    print(f"  {tbl}: {n:,} rows")

print("\n=== Sample analytical view: v_define_defect_rate ===")
for row in cur.execute(
    "SELECT shipping_mode, market, n_orders, ROUND(late_rate,3) FROM v_define_defect_rate ORDER BY late_rate DESC LIMIT 5"):
    print(f"  {row}")

conn.commit()
conn.close()
print(f"\nDB ready at: {DB}")
print(f"Size: {DB.stat().st_size:,} bytes")
