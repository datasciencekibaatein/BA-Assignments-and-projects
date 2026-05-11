"""
Load Google Play Store data into a SQLite database.
Run from project root: python sql/load_data.py
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
SQL_DIR  = ROOT / "sql"
DB_PATH  = ROOT / "outputs" / "playstore.db"

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)

# Schema
schema_sql = (SQL_DIR / "schema.sql").read_text()
for stmt in schema_sql.split(';'):
    stmt = stmt.strip()
    if stmt:
        conn.executescript(stmt + ';')
print("Schema created.")

# Load apps
gp = pd.read_csv(DATA_DIR / "googleplaystore.csv")
gp['price_num'] = pd.to_numeric(
    gp['Price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False),
    errors='coerce'
)

def parse_inst(x):
    if pd.isna(x) or x in ['Free', '0']:
        return None
    s = str(x).replace('+', '').replace(',', '')
    try: return int(s)
    except: return None

def parse_size(x):
    if pd.isna(x) or x == 'Varies with device': return None
    x = str(x)
    if x.endswith('M'): return float(x[:-1])
    if x.endswith('k'): return float(x[:-1]) / 1000
    return None

gp['installs'] = gp['Installs'].map(parse_inst)
gp['reviews_num'] = pd.to_numeric(gp['Reviews'], errors='coerce')
gp['size_mb'] = gp['Size'].map(parse_size)

# Filter and dedupe
gp = gp.dropna(subset=['installs', 'price_num']).copy()
gp = gp[gp['price_num'] < 100].copy()
gp = gp.sort_values('reviews_num', ascending=False).drop_duplicates(subset='App', keep='first').reset_index(drop=True)

# Price buckets
buckets = [
    (1, 'Free',      0.00,   0.00),
    (2, '<$1',       0.01,   0.99),
    (3, '$1-2',      1.00,   1.99),
    (4, '$2-3',      2.00,   2.99),
    (5, '$3-5',      3.00,   4.99),
    (6, '$5-10',     5.00,   9.99),
    (7, '$10-25',   10.00,  24.99),
    (8, '$25+',     25.00, 100.00),
]
pb_df = pd.DataFrame(buckets, columns=['bucket_id', 'bucket_label', 'price_min', 'price_max'])
pb_df.to_sql('price_buckets', conn, if_exists='append', index=False)
print(f"  Loaded price_buckets: {len(pb_df)} rows")

def assign_bucket(price):
    if pd.isna(price): return None
    for bid, _, pmin, pmax in buckets:
        if pmin <= price <= pmax:
            return bid
    return None

gp['bucket_id'] = gp['price_num'].map(assign_bucket)
gp['is_paid'] = (gp['Type'] == 'Paid').astype(int)

# Categories
cat_df = gp.groupby('Category').size().reset_index(name='n_apps').rename(columns={'Category': 'category'})
cat_df.to_sql('app_categories', conn, if_exists='append', index=False)
print(f"  Loaded app_categories: {len(cat_df)} rows")

# Apps
apps_out = pd.DataFrame({
    'app_name':       gp['App'],
    'category':       gp['Category'],
    'rating':         gp['Rating'],
    'n_reviews':      gp['reviews_num'].fillna(0).astype(int),
    'size_mb':        gp['size_mb'],
    'n_installs':     gp['installs'].astype(int),
    'is_paid':        gp['is_paid'],
    'price_usd':      gp['price_num'],
    'bucket_id':      gp['bucket_id'],
    'content_rating': gp['Content Rating'],
    'last_updated':   gp['Last Updated'],
})
apps_out.to_sql('apps', conn, if_exists='append', index=False)
print(f"  Loaded apps: {len(apps_out):,} rows")

# Reviews
revs = pd.read_csv(DATA_DIR / "googleplaystore_user_reviews.csv")
revs = revs.dropna(subset=['Sentiment'])
revs_out = pd.DataFrame({
    'app_name':     revs['App'],
    'sentiment':    revs['Sentiment'],
    'polarity':     revs['Sentiment_Polarity'],
    'subjectivity': revs['Sentiment_Subjectivity'],
})
revs_out.to_sql('app_reviews', conn, if_exists='append', index=False)
print(f"  Loaded app_reviews: {len(revs_out):,} rows")

# Verify views
print("\nValidating views...")
for v in ['v_category_summary', 'v_dupont_decomposition', 'v_funnel_per_app',
          'v_price_band_summary', 'v_app_with_sentiment']:
    n = conn.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0]
    print(f"  {v:<32} {n:>8,} rows")

conn.commit()
conn.close()
print(f"\nDB saved to {DB_PATH} ({DB_PATH.stat().st_size/1024/1024:.1f} MB)")
