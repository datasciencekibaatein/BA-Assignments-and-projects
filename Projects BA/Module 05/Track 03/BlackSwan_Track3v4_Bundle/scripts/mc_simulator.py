#!/usr/bin/env python3
"""
EnergyCo Black Swan Audit — Monte Carlo Risk Simulator (CLI tool)

Calibrates GARCH(1,1) with Student-t residuals on real Brent oil prices,
then runs 10,000 Schwartz mean-reverting Monte Carlo paths to compute the
project NPV distribution. Outputs P5/P50/P95, probability of loss, CVaR,
and Black-Scholes real option values.

Usage:
    python mc_simulator.py --input data/BrentOilPrices.csv --out outputs/
    python mc_simulator.py --input data/BrentOilPrices.csv --out outputs/ --sims 10000
"""
import argparse
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import norm
from math import log, sqrt, exp

# ---------- Project parameters (EnergyCo synthetic anchor) ----------
PROJECT_CAPEX = 150_000_000
PRODUCTION_BBL_DAY = 5_000
PRODUCTION_BBL_MONTH = PRODUCTION_BBL_DAY * 30
EXTRACTION_COST = 35
FIXED_OPEX_YR = 12_000_000
DD_PER_YR = PROJECT_CAPEX / 10
TAX_RATE = 0.21
WACC = 0.0935
N_MONTHS = 120
DAYS_PER_MONTH = 21

# Real options
SALVAGE_VALUE = 40_000_000
EXPANSION_CAPEX = 60_000_000
T_ABANDON = 3.0
T_EXPAND = 5.0


def parse_brent_dates(s):
    for fmt in ('%d-%b-%y', '%b %d, %Y'):
        try: return pd.to_datetime(s, format=fmt)
        except: pass
    return pd.NaT


def calibrate_garch_t(log_returns):
    """Fit GARCH(1,1) with Student-t residuals on percent returns."""
    from arch import arch_model
    log_ret_pct = log_returns * 100
    am = arch_model(log_ret_pct, vol='GARCH', p=1, q=1, dist='t')
    res = am.fit(disp='off')
    return {
        'omega':  float(res.params['omega']),
        'alpha':  float(res.params['alpha[1]']),
        'beta':   float(res.params['beta[1]']),
        'nu':     float(res.params['nu']),
        'persist': float(res.params['alpha[1]'] + res.params['beta[1]']),
    }


def calibrate_schwartz(prices):
    """Fit Schwartz one-factor mean-reverting model (OU on log prices)."""
    log_p = np.log(prices.values)
    dlog = np.diff(log_p)
    # Regress dlog ~ a + b*log_p_lag  →  kappa = -b, log_LR = a/kappa
    log_p_lag = log_p[:-1]
    slope, intercept = np.polyfit(log_p_lag, dlog, 1)
    kappa_d = -slope
    log_LR = intercept / kappa_d if kappa_d != 0 else log_p.mean()
    sigma_d = dlog.std()
    return {
        'kappa_daily': float(kappa_d),
        'log_LR':      float(log_LR),
        'LR_price':    float(np.exp(log_LR)),
        'sigma_daily': float(sigma_d),
        'half_life_days': float(np.log(2)/kappa_d) if kappa_d > 0 else float('inf'),
    }


def simulate_paths(S0, schwartz, nu, n_sims=10_000, n_months=N_MONTHS, seed=42):
    """Schwartz mean-reverting simulation with Student-t innovations."""
    np.random.seed(seed)
    n_days = n_months * DAYS_PER_MONTH
    log_p = np.full(n_sims, np.log(S0))
    log_paths = np.zeros((n_sims, n_days))
    for t in range(n_days):
        z = stats.t.rvs(df=nu, size=n_sims) * np.sqrt((nu - 2) / nu)
        dlog = schwartz['kappa_daily'] * (schwartz['log_LR'] - log_p) + schwartz['sigma_daily'] * z
        log_p = log_p + dlog
        log_paths[:, t] = log_p
    prices = np.exp(log_paths)
    monthly = prices.reshape(n_sims, n_months, DAYS_PER_MONTH).mean(axis=2)
    return prices, monthly


def compute_npv(monthly_prices):
    """Compute project NPV distribution from monthly Brent paths."""
    n_sims, n_months = monthly_prices.shape
    months = np.arange(1, n_months + 1)
    discount = 1 / (1 + WACC/12) ** months
    revenues = monthly_prices * PRODUCTION_BBL_MONTH
    extraction = EXTRACTION_COST * PRODUCTION_BBL_MONTH
    opex_monthly = FIXED_OPEX_YR / 12
    ebitda = revenues - extraction - opex_monthly
    ebit = ebitda - DD_PER_YR/12
    tax_paid = np.maximum(ebit, 0) * TAX_RATE
    nopat = ebit - tax_paid
    fcf = nopat + DD_PER_YR/12
    pv_fcf = (fcf * discount).sum(axis=1)
    npv = pv_fcf - PROJECT_CAPEX
    return npv, fcf


def black_scholes(S, K, T, r, sigma, kind='call'):
    if S <= 0 or T <= 0 or sigma <= 0:
        return max(S - K, 0) if kind == 'call' else max(K - S, 0)
    d1 = (log(S/K) + (r + 0.5*sigma**2)*T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    if kind == 'call':
        return S * norm.cdf(d1) - K * exp(-r*T) * norm.cdf(d2)
    else:
        return K * exp(-r*T) * norm.cdf(-d2) - S * norm.cdf(-d1)


def price_real_options(npv_dist, sigma_brent, r_f=0.045, dampening=0.85):
    """Price abandon (put) and expand (call) options at multiple V scenarios."""
    sigma_proj = sigma_brent * dampening
    p5 = float(np.percentile(npv_dist, 5))
    p25 = float(np.percentile(npv_dist, 25))
    p50 = float(np.percentile(npv_dist, 50))
    mean_npv = float(npv_dist.mean())

    scenarios = {}
    for label, npv_val in [('P5', p5), ('P25', p25), ('Median', p50), ('Mean', mean_npv)]:
        V0 = max(npv_val + PROJECT_CAPEX, 1e6)  # gross PV (floored to avoid div-by-0)
        abandon_put = black_scholes(V0, SALVAGE_VALUE, T_ABANDON, r_f, sigma_proj, 'put')
        # Expand: incremental PV from 50% capacity expansion
        expand_call = black_scholes(0.5 * V0, EXPANSION_CAPEX, T_EXPAND, r_f, sigma_proj, 'call')
        scenarios[label] = {
            'V0_gross_pv': V0,
            'abandon_put': abandon_put,
            'expand_call': expand_call,
            'total': abandon_put + expand_call,
        }
    return {
        'sigma_brent_annualized': sigma_brent,
        'sigma_project_annualized': sigma_proj,
        'r_f': r_f,
        'K_abandon': SALVAGE_VALUE, 'T_abandon': T_ABANDON,
        'K_expand': EXPANSION_CAPEX, 'T_expand': T_EXPAND,
        'scenarios': scenarios,
    }


def black_swan_count(prices):
    """Count >3σ events in simulated returns."""
    log_returns = np.log(prices[:, 1:] / prices[:, :-1])
    sigma_total = log_returns.std()
    n_3sigma = int((np.abs(log_returns) > 3 * sigma_total).sum())
    n_5sigma = int((np.abs(log_returns) > 5 * sigma_total).sum())
    total = int(log_returns.size)
    return {
        'total_observations': total,
        'n_3sigma_events': n_3sigma,
        'n_5sigma_events': n_5sigma,
        'frequency_3sigma': n_3sigma / total,
        'gaussian_baseline': 0.0027,
        'excess_factor': (n_3sigma / total) / 0.0027,
    }


def main():
    ap = argparse.ArgumentParser(description='Black Swan Audit Monte Carlo simulator')
    ap.add_argument('--input', '-i', required=True, help='Brent prices CSV')
    ap.add_argument('--out',   '-o', default='./outputs', help='Output directory')
    ap.add_argument('--sims',  '-n', type=int, default=10_000, help='Number of MC paths')
    ap.add_argument('--seed',  type=int, default=42)
    args = ap.parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f'Loading {args.input}...')
    df = pd.read_csv(args.input)
    df['Date'] = df['Date'].apply(parse_brent_dates)
    df = df.sort_values('Date').reset_index(drop=True)
    df['log_ret'] = np.log(df['Price'] / df['Price'].shift(1))
    df = df.dropna()
    print(f'  Loaded {len(df):,} daily observations')
    print(f'  Date range: {df.Date.min().date()} to {df.Date.max().date()}')
    S0 = float(df['Price'].iloc[-1])
    print(f'  Last spot price: ${S0:.2f}')

    # Calibrate models
    print('\nFitting GARCH(1,1) Student-t...')
    garch = calibrate_garch_t(df['log_ret'])
    print(f"  omega={garch['omega']:.5f}, alpha={garch['alpha']:.4f}, beta={garch['beta']:.4f}, nu={garch['nu']:.2f}")

    print('Calibrating Schwartz mean-reverting model...')
    schwartz = calibrate_schwartz(df['Price'])
    print(f"  kappa(d)={schwartz['kappa_daily']:.5f}, LR=${schwartz['LR_price']:.2f}, σ(d)={schwartz['sigma_daily']:.4f}")
    print(f"  Half-life: {schwartz['half_life_days']:.0f} days ({schwartz['half_life_days']/252:.1f} yrs)")

    # Real Brent statistics
    sigma_annual = df['log_ret'].std() * np.sqrt(252)
    real_stats = {
        'mean_log_return_daily': float(df['log_ret'].mean()),
        'std_log_return_daily':  float(df['log_ret'].std()),
        'annualized_volatility': float(sigma_annual),
        'skewness':              float(df['log_ret'].skew()),
        'excess_kurtosis':       float(df['log_ret'].kurtosis()),
        'min_daily_log_return':  float(df['log_ret'].min()),
        'max_daily_log_return':  float(df['log_ret'].max()),
        'n_observations':        int(len(df)),
        'n_3sigma_real':         int((np.abs(df['log_ret']) > 3*df['log_ret'].std()).sum()),
        'last_spot_price':       S0,
    }

    # Simulate
    print(f'\nSimulating {args.sims:,} × {N_MONTHS} months...')
    prices, monthly = simulate_paths(S0, schwartz, garch['nu'], n_sims=args.sims, seed=args.seed)
    print(f'  Done. Shape: {monthly.shape}')

    # NPV
    print('Computing NPV distribution...')
    npv, fcf = compute_npv(monthly)
    npv_summary = {
        'mean':   float(npv.mean()),
        'median': float(np.median(npv)),
        'std':    float(npv.std()),
        'p5':     float(np.percentile(npv, 5)),
        'p25':    float(np.percentile(npv, 25)),
        'p75':    float(np.percentile(npv, 75)),
        'p95':    float(np.percentile(npv, 95)),
        'min':    float(npv.min()),
        'max':    float(npv.max()),
        'prob_loss':            float((npv < 0).mean()),
        'prob_severe_loss':     float((npv < -50e6).mean()),
        'cvar_5':               float(npv[npv <= np.percentile(npv, 5)].mean()),
    }

    # Black Swan stats
    bs_stats = black_swan_count(prices)

    # Real options
    options = price_real_options(npv, sigma_brent=sigma_annual)

    # Save NPV array, prices, FCF for downstream
    np.save(out_dir / 'npv_distribution.npy', npv)
    np.save(out_dir / 'monthly_prices.npy',   monthly)
    np.save(out_dir / 'fcf_paths.npy',        fcf)

    # Save summary JSON
    summary = {
        'S0': S0,
        'real_brent_stats': real_stats,
        'garch_t_params':    garch,
        'schwartz_params':   schwartz,
        'simulation': {'n_sims': args.sims, 'n_months': N_MONTHS, 'seed': args.seed},
        'npv_summary':       npv_summary,
        'black_swan_simulated': bs_stats,
        'real_options':      options,
    }
    with open(out_dir / 'mc_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    # Print headline
    print('\n' + '='*70)
    print('NPV DISTRIBUTION')
    print('='*70)
    print(f"  Mean:    ${npv_summary['mean']/1e6:>8.1f}M")
    print(f"  Median:  ${npv_summary['median']/1e6:>8.1f}M")
    print(f"  P5:      ${npv_summary['p5']/1e6:>8.1f}M  (P95: ${npv_summary['p95']/1e6:.1f}M)")
    print(f"  Prob(NPV<0):     {npv_summary['prob_loss']*100:>5.2f}%")
    print(f"  CVaR(5%):        ${npv_summary['cvar_5']/1e6:>5.1f}M")
    print(f"\nBlack Swan: {bs_stats['n_3sigma_events']:,} >3σ events in simulation ({bs_stats['excess_factor']:.2f}× Gaussian)")
    print(f"\nReal options (median V0):")
    med = options['scenarios']['Median']
    print(f"  Abandon put:  ${med['abandon_put']/1e6:.2f}M")
    print(f"  Expand call:  ${med['expand_call']/1e6:.2f}M")
    print(f"  TOTAL:        ${med['total']/1e6:.2f}M  ({med['total']/PROJECT_CAPEX*100:.1f}% of CapEx)")
    print(f"\nFull summary: {out_dir / 'mc_summary.json'}")


if __name__ == '__main__':
    main()
