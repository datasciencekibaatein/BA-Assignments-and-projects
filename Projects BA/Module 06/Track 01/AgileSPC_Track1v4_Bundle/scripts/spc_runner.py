#!/usr/bin/env python3
"""SPC + EOQ runner for Track 1 v4.

Usage:
    python spc_runner.py --input data/DataCoSupplyChainDataset.csv --out outputs/

Computes:
    1. Late % overall and by Shipping Mode
    2. X-bar control chart on Standard Class shipment variance (weekly)
    3. EOQ + Safety Stock + ROP for top 10 categories
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np


def parse_args():
    p = argparse.ArgumentParser(description='SPC + EOQ runner for DataCo Smart Supply Chain')
    p.add_argument('--input', '-i', required=True, help='Path to DataCoSupplyChainDataset.csv')
    p.add_argument('--out', '-o', default='outputs', help='Output directory')
    p.add_argument('--order-cost', type=float, default=50.0, help='S, order cost ($/PO)')
    p.add_argument('--holding-pct', type=float, default=0.25, help='H rate (annual % of unit price)')
    p.add_argument('--service-z', type=float, default=1.65, help='Z, service level multiplier (1.65=95%%)')
    p.add_argument('--min-subgroup-n', type=int, default=30, help='Minimum subgroup n for SPC')
    p.add_argument('--quiet', action='store_true')
    return p.parse_args()


def load_data(path):
    df = pd.read_csv(path, encoding='latin-1', low_memory=False)
    df['order_date'] = pd.to_datetime(df['order date (DateOrders)'])
    df['ship_variance'] = df['Days for shipping (real)'] - df['Days for shipment (scheduled)']
    return df


def compute_late_summary(df, log):
    log("=" * 60)
    log("LATE DELIVERY SUMMARY")
    log("=" * 60)
    overall = df['Late_delivery_risk'].mean()
    log(f"Overall late risk: {overall*100:.2f}%")
    log("\nBy Shipping Mode:")
    by_mode = df.groupby('Shipping Mode').agg(
        n=('Late_delivery_risk', 'count'),
        late_pct=('Late_delivery_risk', lambda x: x.mean() * 100),
        avg_var=('ship_variance', 'mean'),
        std_var=('ship_variance', 'std'),
    ).round(3).sort_values('late_pct', ascending=False)
    log(by_mode.to_string())
    return by_mode


def compute_spc(df, min_n, log):
    log("\n" + "=" * 60)
    log("SPC X-BAR CONTROL CHART (Standard Class)")
    log("=" * 60)
    sc = df[df['Shipping Mode'] == 'Standard Class'].copy()
    sc['week'] = sc['order_date'].dt.to_period('W')

    weekly = sc.groupby('week').agg(
        n=('ship_variance', 'count'),
        mean_var=('ship_variance', 'mean'),
        std_var=('ship_variance', 'std'),
    ).reset_index()
    weekly = weekly[weekly['n'] >= min_n].reset_index(drop=True)

    n_med = int(weekly['n'].median())
    xbar_bar = weekly['mean_var'].mean()
    sbar = weekly['std_var'].mean()
    A3 = 3 / np.sqrt(n_med)
    UCL = xbar_bar + A3 * sbar
    LCL = xbar_bar - A3 * sbar

    weekly['out_of_control'] = (weekly['mean_var'] > UCL) | (weekly['mean_var'] < LCL)
    n_out = int(weekly['out_of_control'].sum())

    log(f"Subgroups: {len(weekly)} weeks (median n={n_med})")
    log(f"CL (X-bar-bar): {xbar_bar:.4f}")
    log(f"sbar:           {sbar:.4f}")
    log(f"UCL:            {UCL:.4f}")
    log(f"LCL:            {LCL:.4f}")
    log(f"\nOut-of-control: {n_out}/{len(weekly)} ({100*n_out/len(weekly):.1f}%)")
    log(f"VERDICT: {'NOT IN CONTROL — Special Cause present' if n_out > 0 else 'IN CONTROL — Common Cause only'}")

    return weekly, {'CL': xbar_bar, 'sbar': sbar, 'UCL': UCL, 'LCL': LCL, 'n_out': n_out, 'n_total': len(weekly)}


def compute_eoq(df, S, holding_pct, Z, log):
    log("\n" + "=" * 60)
    log("EOQ + SAFETY STOCK (Top 10 Categories)")
    log("=" * 60)
    months = 36
    days_in_data = months * 30

    top_cats = df.groupby('Category Name').agg(
        total_qty=('Order Item Quantity', 'sum')
    ).sort_values('total_qty', ascending=False).head(10).index.tolist()

    rows = []
    for cat in top_cats:
        sub = df[df['Category Name'] == cat]
        D = sub['Order Item Quantity'].sum() * (12 / months)
        unit_cost = sub['Sales'].sum() / max(sub['Order Item Quantity'].sum(), 1)
        H = holding_pct * unit_cost
        EOQ = np.sqrt(2 * D * S / H) if H > 0 else 0

        d_daily = sub['Order Item Quantity'].sum() / days_in_data
        d_std_daily = sub.groupby(sub['order_date'].dt.date)['Order Item Quantity'].sum().std()
        L_mean = sub['Days for shipping (real)'].mean()
        L_std = sub['Days for shipping (real)'].std()

        SS = Z * np.sqrt(L_mean * d_std_daily ** 2 + d_daily ** 2 * L_std ** 2)
        ROP = d_daily * L_mean + SS

        annual_eoq = (D / EOQ) * S + (EOQ / 2) * H if EOQ > 0 else 0
        Q_sq = D / 4
        annual_sq = (D / Q_sq) * S + (Q_sq / 2) * H if Q_sq > 0 else 0
        savings = annual_sq - annual_eoq

        rows.append({
            'Category': cat,
            'D_annual': round(D),
            'unit_price': round(unit_cost, 2),
            'EOQ': round(EOQ),
            'SS': round(SS),
            'ROP': round(ROP),
            'savings_$': round(savings),
        })

    eoq_df = pd.DataFrame(rows)
    log(eoq_df.to_string(index=False))
    log(f"\nTOTAL ANNUAL SAVINGS: ${eoq_df['savings_$'].sum():,}")
    return eoq_df


def main():
    args = parse_args()

    out_dir = Path(args.out)
    out_dir.mkdir(exist_ok=True, parents=True)

    def log(msg):
        if not args.quiet:
            print(msg)

    log(f"Loading {args.input}...")
    df = load_data(args.input)
    log(f"Loaded {len(df):,} orders, {len(df.columns)} columns")
    log(f"Date range: {df['order_date'].min().date()} → {df['order_date'].max().date()}")

    by_mode = compute_late_summary(df, log)
    weekly, spc_summary = compute_spc(df, args.min_subgroup_n, log)
    eoq_df = compute_eoq(df, args.order_cost, args.holding_pct, args.service_z, log)

    by_mode.to_csv(out_dir / 'late_by_mode.csv')
    weekly.to_csv(out_dir / 'spc_weekly.csv', index=False)
    eoq_df.to_csv(out_dir / 'eoq_safety_stock.csv', index=False)

    import json
    summary = {
        'late_pct_overall': float(df['Late_delivery_risk'].mean()),
        'spc': {k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in spc_summary.items()},
        'eoq_total_savings': int(eoq_df['savings_$'].sum()),
    }
    with open(out_dir / 'run_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    log(f"\nOutputs saved to {out_dir}/")
    log(f"  late_by_mode.csv | spc_weekly.csv | eoq_safety_stock.csv | run_summary.json")
    return 0


if __name__ == '__main__':
    sys.exit(main())
