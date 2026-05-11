#!/usr/bin/env python3
"""
capstress_runner.py — Capital Structure Stress-Test CLI
Reproduces all hero numbers from real FRED + Industrials peer data.

Usage:
    python3 capstress_runner.py --data-dir ../data --out ../outputs
"""
import argparse
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

# Auto-resolve data dir
def find_data_dir(arg_dir=None):
    if arg_dir and Path(arg_dir).exists():
        return Path(arg_dir)
    here = Path(__file__).resolve().parent
    for cand in [here.parent/'data', here/'data', Path.cwd()/'data']:
        if cand.exists():
            return cand
    raise FileNotFoundError("Cannot find data/ directory")


def load_fred(data_dir):
    out = {}
    dgs10 = pd.read_csv(data_dir/'DGS10.csv')
    dgs10 = dgs10[dgs10['DGS10'] != '.'].copy()
    dgs10['DGS10'] = pd.to_numeric(dgs10['DGS10'])
    out['rf'] = float(dgs10['DGS10'].tail(252).mean())
    
    baa = pd.read_csv(data_dir/'BAA.csv')
    out['baa'] = float(baa['BAA'].iloc[-1])
    aaa = pd.read_csv(data_dir/'AAA.csv')
    out['aaa'] = float(aaa['AAA'].iloc[-1])
    out['spread'] = out['baa'] - out['aaa']
    
    cpi = pd.read_csv(data_dir/'CPIAUCSL.csv')
    cpi['YoY'] = cpi['CPIAUCSL'].pct_change(12) * 100
    out['cpi_yoy'] = float(cpi['YoY'].iloc[-1])
    
    ppi = pd.read_csv(data_dir/'PPIACO.csv')
    ppi['YoY'] = ppi['PPIACO'].pct_change(12) * 100
    out['ppi_yoy'] = float(ppi['YoY'].iloc[-1])
    return out


def calibrate_peers(data_dir):
    df = pd.read_csv(data_dir/'2018_Financial_Data.csv')
    ind = df[df['Sector'] == 'Industrials'].copy()
    req = ['Revenue','Total debt','Total shareholders equity','Total assets',
           'Interest Expense','Income Tax Expense','EBITDA','Net Income',
           'Capital Expenditure','Depreciation & Amortization','Earnings before Tax']
    ind = ind.dropna(subset=req).copy()
    ind = ind[(ind['Revenue'] > 100e6) & (ind['Total shareholders equity'] > 0) & (ind['Total debt'] >= 0)].copy()
    ind['DV'] = ind['Total debt'] / (ind['Total debt'] + ind['Total shareholders equity'])
    ind['AT'] = ind['Revenue'] / ind['Total assets']
    ind['NM'] = ind['Net Income'] / ind['Revenue']
    ind['EM'] = ind['EBITDA'] / ind['Revenue']
    ind['Tax'] = ind['Income Tax Expense'] / ind['Earnings before Tax'].replace(0, np.nan)
    return {
        'n': len(ind),
        'DV': float(ind['DV'].median()),
        'AT': float(ind['AT'].median()),
        'NM': float(ind['NM'].median()),
        'EM': float(ind['EM'].median()),
        'Tax': float(ind[ind['Tax'].between(0.05, 0.5)]['Tax'].median()),
    }


def cost_of_equity(rf, peers):
    """CAPM + APT 3-factor → blend."""
    beta = 1.05
    mrp = 5.5
    ke_capm = rf + beta * mrp
    
    # APT
    b_mkt, b_inf, b_cr = 1.05, 0.40, 0.55
    fp_mkt, fp_inf, fp_cr = 5.5, 2.5, 2.0
    ke_apt = rf + b_mkt*fp_mkt + b_inf*fp_inf + b_cr*fp_cr
    
    return {
        'beta': beta, 'mrp': mrp, 'ke_capm': ke_capm,
        'ke_apt': ke_apt, 'ke_blend': (ke_capm + ke_apt) / 2,
    }


def find_optimal_capstruct(rf, kd_pretax, T, ke_levered_peer, peer_dv):
    """MM with taxes → search for D/V minimizing WACC, with rising kd past 40% leverage."""
    de_peer = peer_dv / (1 - peer_dv)
    ke_unlev = (ke_levered_peer + (kd_pretax * (1-T) * de_peer)) / (1 + de_peer * (1-T))
    
    curve = []
    for dv in np.arange(0, 0.71, 0.05):
        de = dv / (1 - dv) if dv < 1 else 999
        kd_dv = kd_pretax * (1 + 5.0 * max(0, dv - 0.40)**2)
        ke_lev = ke_unlev + (ke_unlev - kd_dv) * de * (1-T)
        wacc = (1-dv)*ke_lev + dv*kd_dv*(1-T)
        curve.append((dv, de, kd_dv, ke_lev, wacc))
    
    arr = np.array(curve)
    idx = np.argmin(arr[:, 4])
    return {
        'ke_unlev': ke_unlev,
        'curve': curve,
        'optimal_dv': float(arr[idx, 0]),
        'optimal_wacc': float(arr[idx, 4]),
    }


def project_dcf(wacc, em, T, capex=200e6, rev_y0=1500e6, life=10):
    """10-year FCF (Indirect Method) + terminal value."""
    import numpy_financial as nf
    rev_g = 0.06; da_pct = 0.05; nwc_pct = 0.12
    maint_capex = 0.03; term_g = 0.025
    ramp = [0, 0.5, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    
    cfs = []
    for y in range(life+1):
        if y == 0:
            cfs.append({'year':y, 'rev':0, 'fcf': -capex})
        else:
            rev = rev_y0 * 0.12 * ramp[y] * (1 + rev_g)**(y-1)
            ebitda = rev * em
            ebit = ebitda - rev*da_pct
            nopat = ebit - max(ebit,0)*T
            ocf = nopat + rev*da_pct
            prev_rev = rev_y0*0.12*ramp[y-1]*(1+rev_g)**(max(0,y-2)) if y>1 else 0
            d_nwc = (rev - prev_rev) * nwc_pct
            fcf = ocf - d_nwc - rev*maint_capex
            if y == life:
                tv = fcf * (1 + term_g) / (wacc/100 - term_g)
                fcf += tv
            cfs.append({'year':y, 'rev':rev, 'fcf':fcf})
    
    fcfs = [c['fcf'] for c in cfs]
    irr = nf.irr(fcfs) * 100
    npv = nf.npv(wacc/100, fcfs)
    return {'cfs': cfs, 'irr': float(irr), 'npv': float(npv)}


def fit_garch(brent_path):
    from arch import arch_model
    brent = pd.read_csv(brent_path)
    brent['Date'] = pd.to_datetime(brent['Date'], format='mixed', errors='coerce')
    brent = brent.dropna(subset=['Date']).sort_values('Date')
    brent['Price'] = pd.to_numeric(brent['Price'], errors='coerce')
    brent = brent.dropna(subset=['Price'])
    ret = (np.log(brent['Price']/brent['Price'].shift(1)).dropna() * 100).values
    
    g = arch_model(ret, vol='GARCH', p=1, q=1, dist='Normal', rescale=False)
    res = g.fit(disp='off')
    omega, alpha, beta_ = res.params['omega'], res.params['alpha[1]'], res.params['beta[1]']
    persist = alpha + beta_
    long_run_vol = np.sqrt(omega/(1-persist)) * np.sqrt(252)
    return {
        'n_obs': len(ret),
        'omega': float(omega), 'alpha': float(alpha), 'beta': float(beta_),
        'persistence': float(persist),
        'long_run_vol_ann_pct': float(long_run_vol),
    }


def monte_carlo(wacc, em_base, T, sigma_oil, n_sims=10000, seed=42):
    """10K MC sims → P(IRR < WACC)."""
    import numpy_financial as nf
    rng = np.random.default_rng(seed)
    rev_y0=1500e6; capex=200e6; life=10
    rev_g_mu=0.06; da_pct=0.05; nwc_pct=0.12; maint_capex=0.03; term_g=0.025
    ramp = [0, 0.5, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    
    irrs, npvs = [], []
    for _ in range(n_sims):
        rev_g = rng.normal(rev_g_mu, 0.02)
        em = max(0.05, rng.normal(em_base, 0.025))
        oil_shock = rng.normal(0, sigma_oil * np.sqrt(0.25))
        em_adj = max(0.03, em * (1 - oil_shock * 0.20))
        
        fcfs = [-capex]
        for y in range(1, life+1):
            rev = rev_y0 * 0.12 * ramp[y] * (1 + rev_g)**(y-1)
            ebitda = rev * em_adj
            ebit = ebitda - rev*da_pct
            nopat = ebit - max(ebit,0)*T
            ocf = nopat + rev*da_pct
            prev = rev_y0*0.12*ramp[y-1]*(1+rev_g)**(max(0,y-2)) if y>1 else 0
            fcf = ocf - (rev-prev)*nwc_pct - rev*maint_capex
            if y == life:
                fcf += fcf * (1+term_g) / (wacc/100 - term_g)
            fcfs.append(fcf)
        try:
            irr = nf.irr(fcfs) * 100
            npv = nf.npv(wacc/100, fcfs)
            if not np.isnan(irr):
                irrs.append(irr); npvs.append(npv)
        except: pass
    
    irrs = np.array(irrs); npvs = np.array(npvs)
    return {
        'n_success': len(irrs),
        'irr_mean': float(irrs.mean()), 'irr_median': float(np.median(irrs)),
        'irr_p5': float(np.percentile(irrs,5)), 'irr_p95': float(np.percentile(irrs,95)),
        'prob_irr_below_wacc': float((irrs < wacc).mean() * 100),
        'prob_neg_npv': float((npvs < 0).mean() * 100),
    }


def black_scholes_call(S, K, T, r, sigma):
    """Real option (option to expand)."""
    from scipy.stats import norm
    d1 = (np.log(S/K) + (r + sigma**2/2)*T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return float(S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2))


def main():
    ap = argparse.ArgumentParser(description="Capital structure stress test")
    ap.add_argument('--data-dir', type=str, default=None)
    ap.add_argument('--out', type=str, default='outputs')
    ap.add_argument('--n-sims', type=int, default=10000)
    args = ap.parse_args()
    
    data_dir = find_data_dir(args.data_dir)
    out_dir = Path(args.out); out_dir.mkdir(parents=True, exist_ok=True)
    print(f"Data: {data_dir}")
    print(f"Out:  {out_dir}\n")
    
    print("=== FRED parameters ===")
    fred = load_fred(data_dir)
    print(f"  Rf (1yr DGS10 avg):   {fred['rf']:.3f}%")
    print(f"  BAA yield:            {fred['baa']:.3f}%")
    print(f"  AAA-BAA spread:       {fred['spread']:.3f}%")
    
    print("\n=== Peer calibration (Industrials) ===")
    peers = calibrate_peers(data_dir)
    print(f"  Firms: {peers['n']}, D/V: {peers['DV']:.3f}, Tax: {peers['Tax']:.3f}, EM: {peers['EM']:.3f}")
    
    print("\n=== Cost of equity ===")
    ce = cost_of_equity(fred['rf'], peers)
    print(f"  CAPM Ke:  {ce['ke_capm']:.3f}%")
    print(f"  APT  Ke:  {ce['ke_apt']:.3f}%")
    print(f"  Blend Ke: {ce['ke_blend']:.3f}%")
    
    print("\n=== MM optimal capital structure ===")
    cap = find_optimal_capstruct(fred['rf'], fred['baa'], peers['Tax'], ce['ke_blend'], peers['DV'])
    print(f"  Ke (unlevered):  {cap['ke_unlev']:.3f}%")
    print(f"  Optimal D/V:     {cap['optimal_dv']:.3f}")
    print(f"  Min WACC:        {cap['optimal_wacc']:.3f}%")
    
    print("\n=== Project DCF ===")
    dcf = project_dcf(cap['optimal_wacc'], peers['EM'], peers['Tax'])
    print(f"  IRR: {dcf['irr']:.2f}%   NPV: ${dcf['npv']/1e6:.1f}M")
    
    print("\n=== GARCH on Brent ===")
    g = fit_garch(data_dir/'BrentOilPrices.csv')
    print(f"  α+β persistence: {g['persistence']:.4f}")
    print(f"  Long-run vol:    {g['long_run_vol_ann_pct']:.2f}%")
    
    print(f"\n=== Monte Carlo {args.n_sims:,} sims ===")
    mc = monte_carlo(cap['optimal_wacc'], peers['EM'], peers['Tax'],
                     g['long_run_vol_ann_pct']/100, n_sims=args.n_sims)
    print(f"  IRR P5/P50/P95:        {mc['irr_p5']:.2f}% / {mc['irr_median']:.2f}% / {mc['irr_p95']:.2f}%")
    print(f"  P(IRR < WACC):         {mc['prob_irr_below_wacc']:.2f}%")
    print(f"  P(NPV < 0):            {mc['prob_neg_npv']:.2f}%")
    
    print("\n=== Black-Scholes real option (expand) ===")
    call = black_scholes_call(150e6, 100e6, 5, fred['rf']/100, g['long_run_vol_ann_pct']/100)
    print(f"  Call value:  ${call/1e6:.2f}M")
    
    summary = {
        'fred': fred, 'peers': peers, 'cost_of_equity': ce, 'cap_struct': cap,
        'project': dcf, 'garch': g, 'monte_carlo': mc, 'real_option': call,
    }
    with open(out_dir/'capstress_summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nSaved {out_dir}/capstress_summary.json")


if __name__ == '__main__':
    main()
