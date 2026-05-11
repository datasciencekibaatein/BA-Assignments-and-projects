#!/usr/bin/env python3
"""
DistributorCo Lean Shield - SPC Process Monitor (CLI Tool)

Reads order/shipping data, computes per-mode control charts, applies the
Western Electric rules to flag out-of-control points, computes Cp/Cpk,
and emits a Control Plan-ready report.

Usage:
    python spc_monitor.py --input data.csv --mode "Standard Class" --out outputs/
    python spc_monitor.py --input data.csv --all-modes --out outputs/
    python spc_monitor.py --help

Required CSV columns:
    order date (DateOrders)
    Shipping Mode
    Days for shipping (real)
    Days for shipment (scheduled)
    Late_delivery_risk
    Order Status

Outputs:
    spc_results_<mode>.csv     - per-day xbar, sigma, p_late, rule violations
    spc_summary_<mode>.txt     - capability indices, control limits, alerts
    control_plan.csv           - full Control Plan template (one row per mode)
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
import numpy as np


# ---------------------------------------------------------------------
# SPC math
# ---------------------------------------------------------------------

# A2, D3, D4 constants for X-bar/R charts (Montgomery, Statistical Quality Control)
SPC_CONSTANTS = {
    2:  (1.880, 0.000, 3.267),
    3:  (1.023, 0.000, 2.575),
    4:  (0.729, 0.000, 2.282),
    5:  (0.577, 0.000, 2.114),
    6:  (0.483, 0.000, 2.004),
    7:  (0.419, 0.076, 1.924),
    8:  (0.373, 0.136, 1.864),
    9:  (0.337, 0.184, 1.816),
    10: (0.308, 0.223, 1.777),
}


def get_spc_constants(n):
    """Return (A2, D3, D4) for sample size n. Falls back to nearest entry."""
    if n in SPC_CONSTANTS:
        return SPC_CONSTANTS[n]
    closest = min(SPC_CONSTANTS.keys(), key=lambda k: abs(k - n))
    return SPC_CONSTANTS[closest]


def western_electric_rules(values, centerline, sigma):
    """
    Apply Western Electric rules to a series of values.
    Returns a list of dicts, one per point, with 'violations' = list of rule names.

    Rule 1: any point beyond 3 sigma
    Rule 2: 2 of 3 consecutive points beyond 2 sigma (same side)
    Rule 3: 4 of 5 consecutive points beyond 1 sigma (same side)
    Rule 4: 8 consecutive points on the same side of the centerline
    """
    flags = []
    for i, v in enumerate(values):
        viols = []
        # Rule 1
        if abs(v - centerline) > 3 * sigma:
            viols.append('R1_beyond_3sigma')
        # Rule 2: 2 of last 3 beyond 2 sigma same side
        if i >= 2:
            recent = values[i-2:i+1]
            above = sum(1 for x in recent if x - centerline > 2 * sigma)
            below = sum(1 for x in recent if centerline - x > 2 * sigma)
            if above >= 2 or below >= 2:
                viols.append('R2_2of3_beyond_2sigma')
        # Rule 3: 4 of last 5 beyond 1 sigma same side
        if i >= 4:
            recent = values[i-4:i+1]
            above = sum(1 for x in recent if x - centerline > sigma)
            below = sum(1 for x in recent if centerline - x > sigma)
            if above >= 4 or below >= 4:
                viols.append('R3_4of5_beyond_1sigma')
        # Rule 4: 8 consecutive same side
        if i >= 7:
            recent = values[i-7:i+1]
            if all(x > centerline for x in recent) or all(x < centerline for x in recent):
                viols.append('R4_8_consecutive_same_side')
        flags.append(viols)
    return flags


def compute_capability(real_days, scheduled_days):
    """
    Compute Cp, Cpu, Cpl, Cpk for a process.
    USL = scheduled_days (don't exceed promise), LSL = 0.
    Returns dict with all values; handles sigma=0 (deterministic process).
    """
    n = len(real_days)
    mean = float(np.mean(real_days))
    sigma = float(np.std(real_days, ddof=1)) if n > 1 else 0.0
    USL = float(scheduled_days)
    LSL = 0.0

    if sigma == 0:
        # Deterministic process: Cpk meaningless via formula, return a flag
        return {
            'n': n,
            'mean': mean,
            'sigma': sigma,
            'USL': USL,
            'LSL': LSL,
            'Cp': None,
            'Cpu': None,
            'Cpl': None,
            'Cpk': None,
            'capability_status': 'DETERMINISTIC_PROCESS',
            'note': f'sigma=0; process always delivers in {mean:.0f} days vs scheduled {USL:.0f}'
        }

    Cp = (USL - LSL) / (6 * sigma)
    Cpu = (USL - mean) / (3 * sigma)
    Cpl = (mean - LSL) / (3 * sigma)
    Cpk = min(Cpu, Cpl)

    if Cpk < 0:
        status = 'CRITICAL_OUT_OF_SPEC'
    elif Cpk < 1.0:
        status = 'NOT_CAPABLE'
    elif Cpk < 1.33:
        status = 'MARGINAL'
    elif Cpk < 1.67:
        status = 'CAPABLE'
    else:
        status = 'EXCELLENT'

    return {
        'n': n,
        'mean': mean,
        'sigma': sigma,
        'USL': USL,
        'LSL': LSL,
        'Cp': Cp,
        'Cpu': Cpu,
        'Cpl': Cpl,
        'Cpk': Cpk,
        'capability_status': status,
        'note': ''
    }


# ---------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------

def run_spc_for_mode(df, mode, out_dir):
    """
    Build daily subgroups, compute X-bar/R control limits, p-chart limits,
    flag rule violations. Returns (results_df, capability_dict).
    """
    sub = df[df['Shipping Mode'] == mode].copy()
    if len(sub) == 0:
        return None, None

    sub['order_date'] = pd.to_datetime(sub['order date (DateOrders)']).dt.date

    # Daily subgroups
    daily = sub.groupby('order_date').agg(
        n=('Days for shipping (real)', 'count'),
        xbar=('Days for shipping (real)', 'mean'),
        rng=('Days for shipping (real)', lambda x: x.max() - x.min()),
        p_late=('Late_delivery_risk', 'mean'),
        scheduled=('Days for shipment (scheduled)', 'first'),
    ).reset_index()
    daily = daily[daily['n'] >= 2].reset_index(drop=True)

    # Use median subgroup size for SPC constants
    n_typ = int(daily['n'].median())
    A2, D3, D4 = get_spc_constants(n_typ)

    # X-bar chart limits
    xbar_bar = daily['xbar'].mean()
    R_bar = daily['rng'].mean()
    UCL_x = xbar_bar + A2 * R_bar
    LCL_x = max(0, xbar_bar - A2 * R_bar)

    # R chart limits
    UCL_r = D4 * R_bar
    LCL_r = D3 * R_bar

    # p-chart (proportion late)
    p_bar = daily['p_late'].mean()
    n_avg = daily['n'].mean()
    if p_bar > 0 and p_bar < 1 and n_avg > 0:
        sigma_p = np.sqrt(p_bar * (1 - p_bar) / n_avg)
        UCL_p = min(1.0, p_bar + 3 * sigma_p)
        LCL_p = max(0.0, p_bar - 3 * sigma_p)
    else:
        sigma_p = 0
        UCL_p = p_bar
        LCL_p = p_bar

    # Western Electric rules on X-bar
    sigma_x = R_bar / 2.326  # d2 for n=5
    if sigma_x > 0:
        viols = western_electric_rules(daily['xbar'].values, xbar_bar, sigma_x)
        daily['xbar_violations'] = ['; '.join(v) if v else '' for v in viols]
    else:
        daily['xbar_violations'] = ''

    # Capability
    cap = compute_capability(
        sub['Days for shipping (real)'].values,
        sub['Days for shipment (scheduled)'].iloc[0],
    )
    cap['mode'] = mode
    cap['xbar_bar'] = xbar_bar
    cap['R_bar'] = R_bar
    cap['UCL_x'] = UCL_x
    cap['LCL_x'] = LCL_x
    cap['UCL_r'] = UCL_r
    cap['LCL_r'] = LCL_r
    cap['p_bar'] = p_bar
    cap['UCL_p'] = UCL_p
    cap['LCL_p'] = LCL_p
    cap['n_subgroups'] = len(daily)
    cap['typical_subgroup_size'] = n_typ
    cap['n_violations'] = (daily['xbar_violations'] != '').sum()

    # Persist
    safe_mode = mode.replace(' ', '_').replace('/', '_')
    daily.to_csv(out_dir / f'spc_results_{safe_mode}.csv', index=False)

    summary = format_summary(mode, cap)
    (out_dir / f'spc_summary_{safe_mode}.txt').write_text(summary)

    return daily, cap


def format_summary(mode, cap):
    lines = [
        f"================================================================",
        f"SPC SUMMARY - {mode}",
        f"================================================================",
        f"",
        f"Sample size: {cap['n']:,}",
        f"Subgroups (days):    {cap['n_subgroups']}",
        f"Typical subgroup n:  {cap['typical_subgroup_size']}",
        f"",
        f"--- PROCESS CAPABILITY ---",
        f"  Mean:       {cap['mean']:.3f} days",
        f"  Sigma:      {cap['sigma']:.3f} days",
        f"  USL (sched): {cap['USL']:.0f} days",
        f"  LSL:        {cap['LSL']:.0f} days",
    ]
    if cap['Cpk'] is None:
        lines.append(f"  Cpk:        UNDEFINED ({cap['note']})")
    else:
        lines.extend([
            f"  Cp:         {cap['Cp']:.3f}",
            f"  Cpu:        {cap['Cpu']:.3f}",
            f"  Cpl:        {cap['Cpl']:.3f}",
            f"  Cpk:        {cap['Cpk']:.3f}",
        ])
    lines.append(f"  Status:     {cap['capability_status']}")
    lines.extend([
        f"",
        f"--- X-BAR CHART CONTROL LIMITS ---",
        f"  Centerline (X-bar-bar): {cap['xbar_bar']:.3f}",
        f"  UCL: {cap['UCL_x']:.3f}",
        f"  LCL: {cap['LCL_x']:.3f}",
        f"  R-bar: {cap['R_bar']:.3f}",
        f"",
        f"--- P-CHART (LATE-DELIVERY PROPORTION) ---",
        f"  p-bar:  {cap['p_bar']:.3%}",
        f"  UCL_p:  {cap['UCL_p']:.3%}",
        f"  LCL_p:  {cap['LCL_p']:.3%}",
        f"",
        f"--- ALERTS ---",
        f"  Western Electric rule violations on X-bar: {cap['n_violations']:,} of {cap['n_subgroups']:,} subgroups",
    ])

    if cap['p_bar'] >= 0.50:
        lines.append(f"  >>> CRITICAL: late-delivery rate {cap['p_bar']:.1%} >= 50%; root-cause investigation required")
    elif cap['p_bar'] >= 0.30:
        lines.append(f"  >>> ELEVATED: late-delivery rate {cap['p_bar']:.1%} >= 30%; preventive action recommended")
    else:
        lines.append(f"  >>> WITHIN TOLERANCE: late-delivery rate {cap['p_bar']:.1%}")

    if cap['Cpk'] is not None and cap['Cpk'] < 1.0:
        lines.append(f"  >>> NOT CAPABLE: Cpk = {cap['Cpk']:.3f} < 1.00; process redesign required")

    return '\n'.join(lines)


def write_control_plan(all_caps, out_dir):
    """One row per mode, with control limits and reaction plan."""
    rows = []
    for cap in all_caps:
        rows.append({
            'process': f"Order fulfillment - {cap['mode']}",
            'characteristic': 'Days_to_ship',
            'specification': f"{cap['LSL']:.0f}-{cap['USL']:.0f} days",
            'measurement': 'Auto: order_date - shipping_date',
            'sample_size': f"daily n~{cap['typical_subgroup_size']}",
            'frequency': 'Daily',
            'method': 'X-bar/R + p-chart',
            'centerline_xbar': round(cap['xbar_bar'], 3),
            'UCL_xbar': round(cap['UCL_x'], 3),
            'LCL_xbar': round(cap['LCL_x'], 3),
            'centerline_p': round(cap['p_bar'], 4),
            'UCL_p': round(cap['UCL_p'], 4),
            'LCL_p': round(cap['LCL_p'], 4),
            'Cpk': round(cap['Cpk'], 3) if cap['Cpk'] is not None else 'UNDEFINED',
            'capability_status': cap['capability_status'],
            'reaction_plan': reaction_plan(cap),
            'owner': 'Logistics Manager',
            'review_cadence': 'Weekly',
        })
    cp_df = pd.DataFrame(rows)
    cp_df.to_csv(out_dir / 'control_plan.csv', index=False)


def reaction_plan(cap):
    if cap['capability_status'] == 'DETERMINISTIC_PROCESS' and cap['mean'] > cap['USL']:
        return 'PROCESS DESIGN FAILURE - actual=mean exceeds scheduled deterministically. Renegotiate carrier SLA OR change scheduled commitment.'
    if cap['Cpk'] is not None and cap['Cpk'] < 0:
        return 'CRITICAL OUT-OF-SPEC - process mean violates spec. Stop production, root-cause, redesign.'
    if cap['Cpk'] is not None and cap['Cpk'] < 1.0:
        return 'NOT CAPABLE - reduce variance via carrier vetting + queue-priority changes. Targeting Cpk >= 1.33.'
    if cap['Cpk'] is not None and cap['Cpk'] < 1.33:
        return 'MARGINAL - monitor for drift; flag any 8 consecutive same-side points.'
    return 'CAPABLE - maintain monitoring; investigate any rule violations.'


def main():
    parser = argparse.ArgumentParser(description='SPC Process Monitor for fulfillment data')
    parser.add_argument('--input', '-i', required=True, help='Input CSV path')
    parser.add_argument('--mode', '-m', help='Single shipping mode to analyze')
    parser.add_argument('--all-modes', action='store_true', help='Analyze all shipping modes')
    parser.add_argument('--out', '-o', default='./spc_outputs', help='Output directory')
    args = parser.parse_args()

    if not args.mode and not args.all_modes:
        parser.error('Specify --mode or --all-modes')

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading {args.input}...")
    try:
        df = pd.read_csv(args.input, encoding='latin-1')
    except UnicodeDecodeError:
        df = pd.read_csv(args.input)

    df = df[df['Order Status'].isin(['COMPLETE', 'CLOSED', 'PROCESSING', 'PENDING'])].copy()
    print(f"  Loaded {len(df):,} valid orders")

    if args.all_modes:
        modes = df['Shipping Mode'].dropna().unique().tolist()
    else:
        modes = [args.mode]

    all_caps = []
    for mode in modes:
        print(f"\nAnalyzing: {mode}...")
        daily, cap = run_spc_for_mode(df, mode, out_dir)
        if cap is None:
            print(f"  No data for {mode}, skipping")
            continue
        all_caps.append(cap)
        print(f"  n={cap['n']:,}, Cpk={cap['Cpk']}, p_late={cap['p_bar']:.1%}, status={cap['capability_status']}")
        print(f"  Outputs: spc_results_{mode.replace(' ','_')}.csv + spc_summary_{mode.replace(' ','_')}.txt")

    if all_caps:
        write_control_plan(all_caps, out_dir)
        print(f"\nControl Plan written: {out_dir / 'control_plan.csv'}")

    print(f"\nDone. {len(all_caps)} mode(s) analyzed.")


if __name__ == '__main__':
    main()
