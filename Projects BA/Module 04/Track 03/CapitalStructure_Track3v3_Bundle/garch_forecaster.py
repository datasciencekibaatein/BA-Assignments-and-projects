#!/usr/bin/env python3
"""
GARCH-based Volatility Forecasting Script
==========================================

Standalone CLI tool for fitting GARCH(1,1) Student-t models on
commodity price time series and producing forward volatility cones.

Usage:
    python garch_forecaster.py --input PATH_TO_CSV [options]

Required CSV format:
    Date,Price
    1987-05-20,18.63
    ...

Outputs:
    - garch_diagnostics.csv:  fit parameters, persistence, half-life
    - garch_conditional_vol.csv:  per-day conditional volatility (annualized)
    - garch_forward_cone.csv:    H-day forward forecast (mean + 5/95% bands)
    - garch_summary.txt:         human-readable report
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

try:
    from arch import arch_model
except ImportError:
    print("Required package 'arch' not installed. Run: pip install arch")
    sys.exit(1)


def parse_args():
    p = argparse.ArgumentParser(description="GARCH(1,1) Student-t volatility forecasting")
    p.add_argument("--input", required=True, help="Path to CSV with Date,Price columns")
    p.add_argument("--horizon", type=int, default=90, help="Forecast horizon in days (default 90)")
    p.add_argument("--output-dir", default="garch_outputs", help="Output directory")
    p.add_argument("--annualization", type=int, default=252, help="Trading days per year")
    return p.parse_args()


def load_prices(path):
    """Load and clean price series."""
    df = pd.read_csv(path)
    if 'Date' not in df.columns or 'Price' not in df.columns:
        raise ValueError(f"CSV must have Date,Price columns. Got: {list(df.columns)}")
    df['Date'] = pd.to_datetime(df['Date'], format='mixed', dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Date']).sort_values('Date').reset_index(drop=True)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
    df = df.dropna(subset=['Price'])
    df['log_return'] = np.log(df['Price']).diff()
    return df


def fit_garch(returns_pct):
    """Fit GARCH(1,1) Student-t with constant mean."""
    am = arch_model(returns_pct, vol='Garch', p=1, q=1, dist='StudentsT', mean='Constant')
    res = am.fit(disp='off')
    return res


def main():
    args = parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print(f"Loading {args.input}...")
    df = load_prices(args.input)
    print(f"  {len(df):,} observations from {df['Date'].min().date()} to {df['Date'].max().date()}")
    print(f"  Span: {(df['Date'].max() - df['Date'].min()).days/365.25:.1f} years")

    returns = df['log_return'].dropna() * 100  # in percent
    print(f"  Sample mean: {returns.mean():.4f}%/day, sample std: {returns.std():.4f}%/day")
    sample_vol_ann = returns.std() * np.sqrt(args.annualization)
    print(f"  Sample annualized vol: {sample_vol_ann:.2f}%")

    # Fit GARCH
    print(f"\nFitting GARCH(1,1) Student-t...")
    res = fit_garch(returns)
    omega = res.params['omega']
    alpha = res.params['alpha[1]']
    beta = res.params['beta[1]']
    nu = res.params['nu']
    persistence = alpha + beta
    half_life = -np.log(2)/np.log(persistence) if persistence < 1 else np.inf
    long_run_var = omega/(1-persistence) if persistence < 1 else None
    long_run_vol_ann = np.sqrt(long_run_var * args.annualization) if long_run_var else None

    # Forecast
    print(f"Generating {args.horizon}-day forward forecast...")
    fc = res.forecast(horizon=args.horizon, reindex=False)
    fwd_var = fc.variance.values[-1]
    fwd_vol_daily = np.sqrt(fwd_var)
    fwd_vol_ann = fwd_vol_daily * np.sqrt(args.annualization)

    # Quantiles via Student-t innovations
    from scipy.stats import t as student_t
    p05 = student_t.ppf(0.05, df=nu) * fwd_vol_daily
    p95 = student_t.ppf(0.95, df=nu) * fwd_vol_daily

    # Diagnostics
    diag = pd.DataFrame([{
        'parameter': 'omega', 'value': omega, 'unit': '(%)^2'
    },{
        'parameter': 'alpha[1]', 'value': alpha, 'unit': '-'
    },{
        'parameter': 'beta[1]', 'value': beta, 'unit': '-'
    },{
        'parameter': 'persistence (alpha+beta)', 'value': persistence, 'unit': '-'
    },{
        'parameter': 'half_life_days', 'value': half_life, 'unit': 'days'
    },{
        'parameter': 'long_run_vol_annualized', 'value': long_run_vol_ann, 'unit': '%'
    },{
        'parameter': 'student_t_df (nu)', 'value': nu, 'unit': '-'
    },{
        'parameter': 'sample_vol_annualized', 'value': sample_vol_ann, 'unit': '%'
    },{
        'parameter': 'log_likelihood', 'value': res.loglikelihood, 'unit': '-'
    },{
        'parameter': 'aic', 'value': res.aic, 'unit': '-'
    },{
        'parameter': 'bic', 'value': res.bic, 'unit': '-'
    }])
    diag.to_csv(out_dir / "garch_diagnostics.csv", index=False)

    # Conditional vol time series
    cond_vol_ann = res.conditional_volatility * np.sqrt(args.annualization)
    cv_df = pd.DataFrame({
        'date': df['Date'].iloc[1:].dt.strftime('%Y-%m-%d').values,
        'log_return': returns.values / 100,
        'cond_vol_annualized_pct': cond_vol_ann.values,
    })
    cv_df.to_csv(out_dir / "garch_conditional_vol.csv", index=False)

    # Forward cone
    last_date = df['Date'].max()
    cone = pd.DataFrame({
        'days_ahead': np.arange(1, args.horizon+1),
        'date_proj':  pd.bdate_range(last_date + pd.Timedelta(days=1), periods=args.horizon).strftime('%Y-%m-%d'),
        'cond_vol_daily_pct': fwd_vol_daily,
        'cond_vol_annualized_pct': fwd_vol_ann,
        'p05_daily_return_pct': p05,
        'p95_daily_return_pct': p95,
    })
    cone.to_csv(out_dir / "garch_forward_cone.csv", index=False)

    # Human report
    report = []
    report.append("="*70)
    report.append("GARCH(1,1) Student-t Volatility Forecast Report")
    report.append("="*70)
    report.append(f"\nInput: {args.input}")
    report.append(f"Observations: {len(df):,}")
    report.append(f"Date range:   {df['Date'].min().date()}  ->  {df['Date'].max().date()}")
    report.append(f"Span:         {(df['Date'].max() - df['Date'].min()).days/365.25:.1f} years")
    report.append(f"\n--- Fit parameters ---")
    report.append(f"  omega                         {omega:.6f} (%)^2")
    report.append(f"  alpha[1]                      {alpha:.4f}")
    report.append(f"  beta[1]                       {beta:.4f}")
    report.append(f"  Persistence (alpha+beta)      {persistence:.4f}")
    report.append(f"  Volatility half-life          {half_life:.1f} days")
    report.append(f"  Long-run vol (annualized)     {long_run_vol_ann:.2f}%")
    report.append(f"  Student-t df                  {nu:.2f}")
    report.append(f"  Sample vol (annualized)       {sample_vol_ann:.2f}%")
    report.append(f"\n--- Goodness of fit ---")
    report.append(f"  Log-likelihood   {res.loglikelihood:>10.0f}")
    report.append(f"  AIC              {res.aic:>10.0f}")
    report.append(f"  BIC              {res.bic:>10.0f}")
    report.append(f"\n--- {args.horizon}-day forward vol cone ---")
    for d in [1, 5, 10, 30, 60, args.horizon]:
        if d <= args.horizon:
            report.append(f"  Day {d:>3}:  {fwd_vol_ann[d-1]:.2f}% annualized")
    report.append(f"\nOutputs written to: {out_dir}/")
    report.append(f"  garch_diagnostics.csv      ({len(diag)} rows)")
    report.append(f"  garch_conditional_vol.csv  ({len(cv_df):,} rows)")
    report.append(f"  garch_forward_cone.csv     ({len(cone)} rows)")
    report.append(f"  garch_summary.txt          (this report)")
    report_text = "\n".join(report)
    (out_dir / "garch_summary.txt").write_text(report_text)
    print("\n" + report_text)


if __name__ == "__main__":
    main()
