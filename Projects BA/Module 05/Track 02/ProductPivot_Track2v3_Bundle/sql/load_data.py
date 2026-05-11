"""
Loads IBM Telco Customer Churn CSV into SQLite using schema.sql.
Auto-resolves project root by folder name OR by sibling dirs.
"""
import os
import sys
import sqlite3
import pandas as pd
from pathlib import Path


def find_project_root():
    cwd = Path(__file__).resolve().parent
    for p in [cwd, cwd.parent, cwd.parent.parent, cwd.parent.parent.parent]:
        if (p / 'sql').exists() and (p / 'sql' / 'schema.sql').exists():
            return p
    return cwd.parent


ROOT = find_project_root()
DATA = ROOT / 'data' / 'WA_Fn-UseC_-Telco-Customer-Churn.csv'
SCHEMA = ROOT / 'sql' / 'schema.sql'
OUTPUTS = ROOT / 'outputs'
OUTPUTS.mkdir(exist_ok=True)
DB = OUTPUTS / 'pivotco.db'

print(f"Project root: {ROOT}")
print(f"Data:    {DATA}  exists={DATA.exists()}")
print(f"Schema:  {SCHEMA}")
print(f"DB:      {DB}")

# Read & clean
print("\nReading IBM Telco Customer Churn CSV...")
df = pd.read_csv(DATA)
print(f"  Loaded {len(df):,} rows x {len(df.columns)} columns")

# Coerce TotalCharges (11 blank-space rows for new tenure=0 customers)
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
n_coerced = df['TotalCharges'].isna().sum()
print(f"  TotalCharges: {n_coerced} rows coerced to NULL (all tenure=0 customers)")

# Derive features_adopted
features = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
            'TechSupport', 'StreamingTV', 'StreamingMovies']
df['features_adopted'] = sum((df[f] == 'Yes').astype(int) for f in features)

# Derive tenure_bucket (AAARRR funnel stages)
def tenure_bucket(t):
    if t <= 6:    return '0-6mo (Awareness)'
    if t <= 12:   return '7-12mo (Activation)'
    if t <= 24:   return '13-24mo (Engagement)'
    if t <= 48:   return '25-48mo (Retention)'
    return '49-72mo (Advocacy)'

df['tenure_bucket'] = df['tenure'].apply(tenure_bucket)
df['churn_flag'] = (df['Churn'] == 'Yes').astype(int)

# Connect and rebuild
if DB.exists():
    DB.unlink()
conn = sqlite3.connect(DB)
cur = conn.cursor()

print("\nApplying schema...")
schema_sql = SCHEMA.read_text()
cur.executescript(schema_sql)
conn.commit()

# dim_subscriber
print("\nLoading dim_subscriber...")
dim_s = df[['customerID', 'gender', 'SeniorCitizen', 'Partner', 'Dependents']].drop_duplicates(subset=['customerID'])
dim_s.columns = ['customer_id', 'gender', 'senior_citizen', 'has_partner', 'has_dependents']
dim_s.to_sql('dim_subscriber', conn, if_exists='append', index=False)
print(f"  dim_subscriber: {len(dim_s):,} rows")

# dim_contract
print("Loading dim_contract...")
dim_c = pd.DataFrame({
    'contract_type':      ['Month-to-month', 'One year', 'Two year'],
    'avg_lock_in_months': [1, 12, 24],
    'commitment_tier':    ['Low', 'Medium', 'High'],
})
dim_c.to_sql('dim_contract', conn, if_exists='append', index=False)
print(f"  dim_contract: {len(dim_c)} rows")

# dim_payment
print("Loading dim_payment...")
dim_p = pd.DataFrame({
    'payment_method':  ['Bank transfer (automatic)', 'Credit card (automatic)',
                         'Electronic check', 'Mailed check'],
    'is_automatic':    [1, 1, 0, 0],
    'friction_score':  [2, 1, 5, 4],
})
dim_p.to_sql('dim_payment', conn, if_exists='append', index=False)
print(f"  dim_payment: {len(dim_p)} rows")

# fact_customer_state
print("Loading fact_customer_state...")
fact = df[['customerID', 'tenure', 'MonthlyCharges', 'TotalCharges',
           'Contract', 'PaymentMethod', 'PaperlessBilling',
           'PhoneService', 'MultipleLines', 'InternetService',
           'OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
           'TechSupport', 'StreamingTV', 'StreamingMovies',
           'features_adopted', 'tenure_bucket', 'Churn', 'churn_flag']].copy()
fact.columns = ['customer_id', 'tenure_months', 'monthly_charges', 'total_charges',
                'contract_type', 'payment_method', 'paperless_billing',
                'has_phone', 'has_multiple_lines', 'internet_service',
                'has_online_security', 'has_online_backup', 'has_device_protection',
                'has_tech_support', 'has_streaming_tv', 'has_streaming_movies',
                'features_adopted', 'tenure_bucket', 'churn', 'churn_flag']
fact.to_sql('fact_customer_state', conn, if_exists='append', index=False)
print(f"  fact_customer_state: {len(fact):,} rows")

# Verify
print("\n=== Verification ===")
for tbl in ['dim_subscriber', 'dim_contract', 'dim_payment', 'fact_customer_state']:
    n = cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
    print(f"  {tbl}: {n:,} rows")

print("\n=== Sample analytical view: v_churn_by_contract ===")
for row in cur.execute("SELECT contract_type, n, ROUND(churn_rate,3), ROUND(expected_lifetime_months,1), ROUND(expected_ltv,0) FROM v_churn_by_contract"):
    print(f"  {row}")

print("\n=== Sample: v_funnel_by_tenure ===")
for row in cur.execute("SELECT tenure_bucket, n, ROUND(churn_rate,3) FROM v_funnel_by_tenure ORDER BY churn_rate DESC"):
    print(f"  {row}")

print("\n=== Sample: v_stp_segments ===")
for row in cur.execute("SELECT segment, n, ROUND(churn_rate,3), ROUND(avg_monthly,0), ROUND(estimated_ltv,0) FROM v_stp_segments ORDER BY estimated_ltv DESC"):
    print(f"  {row}")

conn.commit()
conn.close()
print(f"\nDB ready at: {DB}")
print(f"Size: {DB.stat().st_size:,} bytes")
