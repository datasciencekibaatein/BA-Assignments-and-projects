"""
Load Brent oil prices + GARCH outputs + leverage scenarios into a SQLite DB.
Run from project root: python sql/load_data.py
"""
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from arch import arch_model
import warnings; warnings.filterwarnings("ignore")

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
SQL_DIR  = ROOT / "sql"
DB_PATH  = ROOT / "outputs" / "capaudit.db"

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

# === Brent prices ===
df = pd.read_csv(DATA_DIR / "BrentOilPrices.csv")
df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=True, errors='coerce')
df = df.dropna(subset=['Date']).sort_values('Date').reset_index(drop=True)
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df['log_return'] = np.log(df['Price']).diff()

# Fit GARCH and get conditional vol
returns_pct = df['log_return'].dropna() * 100
am = arch_model(returns_pct, vol='Garch', p=1, q=1, dist='StudentsT', mean='Constant')
res = am.fit(disp='off')
cond_vol_ann = res.conditional_volatility * np.sqrt(252)  # annualized %

# Align cond_vol back to df (skip first row since first return is NaN)
df['cond_vol_ann'] = np.nan
df.loc[df.index[1:], 'cond_vol_ann'] = cond_vol_ann.values

# Insert into brent_prices
brent_out = pd.DataFrame({
    'price_date': df['Date'].dt.strftime('%Y-%m-%d'),
    'price_usd':  df['Price'],
    'log_return': df['log_return'],
    'cond_vol_ann': df['cond_vol_ann'],
})
brent_out.to_sql('brent_prices', conn, if_exists='append', index=False)
print(f"  Loaded brent_prices: {len(brent_out):,} rows")

# === Vol regimes ===
regimes = [
    (1, 'LOW',     0.0,  28.0,  'Calm market - GARCH cond vol < 28% annualized'),
    (2, 'MEDIUM', 28.0,  37.0,  'Typical regime - 28-37%'),
    (3, 'HIGH',   37.0,  60.0,  'Elevated stress - 37-60%'),
    (4, 'CRISIS', 60.0, 999.0,  'Crisis regime - GARCH cond vol > 60%'),
]
reg_df = pd.DataFrame(regimes, columns=['regime_id','regime_label','vol_lower','vol_upper','description'])
reg_df.to_sql('vol_regimes', conn, if_exists='append', index=False)
print(f"  Loaded vol_regimes: {len(reg_df)} rows")

# === Leverage scenarios ===
EnergyCo = {'tax_rate': 0.25, 'risk_free': 0.045, 'pre_tax_cod': 0.065}
beta_brent = 0.85
brent_rp = 0.07
V_unlevered = 75e9
beta_U = beta_brent / (1 + (1-EnergyCo['tax_rate'])*0.35)

lev_rows = []
for sid, dv in enumerate([0.0, 0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70], start=1):
    if dv == 0:
        debt = 0; de = 0; tax_shield = 0; V_lev = V_unlevered
        beta_L = beta_U
        ke_lev = EnergyCo['risk_free'] + beta_L * brent_rp
        kd = EnergyCo['pre_tax_cod']
        wacc = ke_lev
    else:
        debt = V_unlevered * dv / (1 - dv)
        de = dv / (1 - dv)
        tax_shield = EnergyCo['tax_rate'] * debt
        V_lev = V_unlevered + tax_shield
        distress_premium = 0.02 * (dv / 0.5)**2 if dv > 0.3 else 0
        kd = EnergyCo['pre_tax_cod'] + distress_premium
        beta_L = beta_U * (1 + (1-EnergyCo['tax_rate']) * de)
        ke_lev = EnergyCo['risk_free'] + beta_L * brent_rp
        wacc = (1-dv)*ke_lev + dv*kd*(1-EnergyCo['tax_rate'])
    lev_rows.append({
        'scenario_id': sid, 'dv_ratio': dv, 'de_ratio': de,
        'debt_amount': debt, 'tax_shield': tax_shield, 'v_levered': V_lev,
        'beta_levered': beta_L, 'ke_pct': ke_lev, 'kd_pct': kd, 'wacc_pct': wacc,
    })
lev_df = pd.DataFrame(lev_rows)
lev_df.to_sql('leverage_scenarios', conn, if_exists='append', index=False)
print(f"  Loaded leverage_scenarios: {len(lev_df)} rows")

# Verify views
print("\nValidating views...")
for v in ['v_yearly_brent_summary','v_decade_vol_clusters','v_vol_regime_freq','v_optimal_leverage','v_extreme_returns']:
    n = conn.execute(f"SELECT COUNT(*) FROM {v}").fetchone()[0]
    print(f"  {v:<30} {n:>6,} rows")

conn.commit()
conn.close()
print(f"\nDB saved to {DB_PATH} ({DB_PATH.stat().st_size/1024/1024:.1f} MB)")
