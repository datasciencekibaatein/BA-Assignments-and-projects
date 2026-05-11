#!/usr/bin/env python3
"""Pirate Growth runner for Track 2 v4.

Usage:
    python pirate_runner.py --input data/online_retail_II.xlsx --out outputs/

Computes:
    1. AARRR funnel (Acquisition, Activation, Retention, Revenue)
    2. Cohort retention matrix
    3. Market Basket Analysis (top 15 rules by lift)
    4. RFM Segmentation (6 segments)
    5. Game Theory Nash equilibrium
    6. Decision Tree EV (Pricing vs Referral)
"""

import argparse
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np
from collections import Counter
from itertools import combinations


def parse_args():
    p = argparse.ArgumentParser(description='Pirate Growth runner for Online Retail II')
    p.add_argument('--input', '-i', required=True, help='Path to online_retail_II.xlsx')
    p.add_argument('--out', '-o', default='outputs', help='Output directory')
    p.add_argument('--gross-margin', type=float, default=0.45, help='Gross margin %')
    p.add_argument('--cac', type=float, default=15.0, help='CAC benchmark (GBP)')
    p.add_argument('--quiet', action='store_true')
    return p.parse_args()


def load_data(path):
    y1 = pd.read_excel(path, sheet_name='Year 2009-2010')
    y2 = pd.read_excel(path, sheet_name='Year 2010-2011')
    df = pd.concat([y1, y2], ignore_index=True)
    df.columns = [c.replace(' ', '_') for c in df.columns]
    clean = df[(df['Customer_ID'].notna()) & (df['Quantity'] > 0) & (df['Price'] > 0)].copy()
    clean['Customer_ID'] = clean['Customer_ID'].astype(int)
    clean['StockCode'] = clean['StockCode'].astype(str)
    clean['Revenue'] = clean['Quantity'] * clean['Price']
    clean['order_month'] = clean['InvoiceDate'].dt.to_period('M')
    return clean


def compute_aarrr(clean, log):
    log("\n=== AARRR FUNNEL ===")
    clean_sorted = clean.sort_values(['Customer_ID', 'InvoiceDate'])
    cust_invoices = clean_sorted.groupby(['Customer_ID', 'Invoice'])['InvoiceDate'].min().reset_index()
    cust_invoices = cust_invoices.sort_values(['Customer_ID', 'InvoiceDate'])
    cust_invoices['order_rank'] = cust_invoices.groupby('Customer_ID').cumcount() + 1

    first_inv = cust_invoices[cust_invoices['order_rank'] == 1][['Customer_ID', 'InvoiceDate']].rename(columns={'InvoiceDate': 'first_inv'})
    second_inv = cust_invoices[cust_invoices['order_rank'] == 2][['Customer_ID', 'InvoiceDate']].rename(columns={'InvoiceDate': 'second_inv'})
    fs = first_inv.merge(second_inv, on='Customer_ID', how='left')
    fs['days_to_2nd'] = (fs['second_inv'] - fs['first_inv']).dt.days

    n_total = len(fs)
    n_30d = (fs['days_to_2nd'] <= 30).sum()
    n_90d = (fs['days_to_2nd'] <= 90).sum()

    log(f"  Acquisition (signups): {n_total}")
    log(f"  Activation (<=30d):    {n_30d} ({100*n_30d/n_total:.1f}%)")
    log(f"  Activation (<=90d):    {n_90d} ({100*n_90d/n_total:.1f}%)")

    return {'signups': n_total, 'activated_30d': int(n_30d), 'activated_90d': int(n_90d),
            'activation_rate_30d': float(n_30d / n_total)}


def compute_cohort(clean, log):
    log("\n=== COHORT RETENTION ===")
    first_order = clean.groupby('Customer_ID')['order_month'].min().reset_index()
    first_order.columns = ['Customer_ID', 'cohort_month']
    cwc = clean.merge(first_order, on='Customer_ID')
    cwc['months_since'] = (cwc['order_month'] - cwc['cohort_month']).apply(lambda x: x.n)
    mat = cwc.groupby(['cohort_month', 'months_since'])['Customer_ID'].nunique().unstack()
    pct = mat.div(mat[0], axis=0) * 100
    avg = pct.mean(axis=0)
    log(f"  Avg M+1:  {avg.get(1, 0):.1f}%")
    log(f"  Avg M+12: {avg.get(12, 0):.1f}%")
    return pct, {f'M{m}': float(avg.get(m, 0)) for m in [1, 3, 6, 12]}


def compute_basket(clean, log):
    log("\n=== MARKET BASKET ANALYSIS ===")
    top = clean['StockCode'].value_counts().head(50).index.tolist()
    mb = clean[clean['StockCode'].isin(top)]
    baskets = mb.groupby('Invoice')['StockCode'].apply(set).reset_index()
    baskets = baskets[baskets['StockCode'].apply(len) >= 2]
    pair_cnt = Counter()
    item_cnt = Counter()
    total = len(baskets)
    for items in baskets['StockCode']:
        for it in items:
            item_cnt[it] += 1
        for pair in combinations(sorted(items, key=str), 2):
            pair_cnt[pair] += 1

    rules = []
    for pair, cnt in pair_cnt.most_common(300):
        if cnt < 50:
            continue
        a, b = pair
        sup = cnt / total
        conf = cnt / item_cnt[a]
        lift = conf / (item_cnt[b] / total)
        rules.append({'A': a, 'B': b, 'support': round(sup, 4),
                      'confidence': round(conf, 3), 'lift': round(lift, 2), 'count': cnt})
    rules_df = pd.DataFrame(rules).sort_values('lift', ascending=False).head(15)
    log(f"  Top rule lift: {rules_df.iloc[0]['lift']:.2f}x")
    log(f"  Mean lift top 5: {rules_df['lift'].head(5).mean():.2f}x")
    return rules_df


def compute_rfm(clean, log):
    log("\n=== RFM SEGMENTATION ===")
    ref = clean['InvoiceDate'].max()
    rfm = clean.groupby('Customer_ID').agg(
        recency=('InvoiceDate', lambda x: (ref - x.max()).days),
        frequency=('Invoice', 'nunique'),
        monetary=('Revenue', 'sum')
    ).reset_index()
    rfm['R'] = pd.qcut(rfm['recency'], 4, labels=[4, 3, 2, 1])
    rfm['F'] = pd.qcut(rfm['frequency'].rank(method='first'), 4, labels=[1, 2, 3, 4])
    rfm['M'] = pd.qcut(rfm['monetary'], 4, labels=[1, 2, 3, 4])

    def seg(row):
        r, f, m = int(row['R']), int(row['F']), int(row['M'])
        if r >= 3 and f >= 3 and m >= 3:
            return 'Champions'
        elif r >= 3 and f >= 2:
            return 'Loyal'
        elif r >= 3 and f <= 2:
            return 'New/Promising'
        elif r <= 2 and f >= 3 and m >= 3:
            return 'At-Risk-VIP'
        elif r <= 2 and f >= 2:
            return 'At-Risk'
        else:
            return 'Hibernating'

    rfm['segment'] = rfm.apply(seg, axis=1)
    summary = rfm.groupby('segment').agg(
        n=('Customer_ID', 'count'),
        mean_LTV=('monetary', 'mean'),
        total_LTV=('monetary', 'sum')
    ).round(0)
    log(summary.to_string())
    return rfm, summary


def compute_game_theory(log):
    log("\n=== GAME THEORY: 2-FIRM NASH ===")
    total_mkt = 35_000_000

    def payoff(oc, tc):
        m_us = 0.45 * (1 + oc / 2)
        m_th = 0.45 * (1 + tc / 2)
        adv = (tc - oc) * 100 / 7
        s_us = max(0.20, min(0.80, 0.5 + 0.05 * adv))
        avg = (oc + tc) / 2
        vol = total_mkt * (1 + 1.2 * abs(avg))
        return vol * s_us * (1 + oc) * m_us / 0.45, vol * (1 - s_us) * (1 + tc) * m_th / 0.45

    strategies = [('Hold', 0), ('Cut7', -0.07), ('Cut15', -0.15)]
    nash = []
    for us, oc in strategies:
        for ts, tc in strategies:
            u, v = payoff(oc, tc)
            us_imp = any(payoff(s[1], tc)[0] > u + 1 for s in strategies)
            th_imp = any(payoff(oc, s[1])[1] > v + 1 for s in strategies)
            if not us_imp and not th_imp:
                nash.append({'us': us, 'them': ts, 'us_payoff_M': round(u/1e6, 2), 'them_payoff_M': round(v/1e6, 2)})

    for n in nash:
        log(f"  NASH: ({n['us']}, {n['them']}) = £{n['us_payoff_M']}M / £{n['them_payoff_M']}M")
    return nash


def compute_decision_tree(clean, gross_margin, cac, log):
    log("\n=== DECISION TREE EV ===")
    n = clean['Customer_ID'].nunique()
    mean_ltv = clean.groupby('Customer_ID')['Revenue'].sum().mean()
    annual_rev = mean_ltv / 2

    # Pricing
    p_scenarios = [(0.30, -0.15, 0.18, 0.10), (0.50, -0.07, 0.084, 0.04), (0.20, -0.03, 0.036, 0.01)]
    ev_p = 0
    for prob, dp, dq, da in p_scenarios:
        rev_chg = (1 + dp) * (1 + dq) - 1
        new_m = gross_margin * (1 + dp / 2)
        new_n = n * (1 + da)
        delta = new_n * annual_rev * (1 + rev_chg) * new_m - n * annual_rev * gross_margin
        ev_p += prob * delta

    # Referral
    r_scenarios = [(0.20, 0.30), (0.50, 0.20), (0.30, 0.10)]
    ev_r = 0
    for prob, k in r_scenarios:
        new_via = n * k
        contrib = new_via * annual_rev * gross_margin
        saved = new_via * (cac - 5)
        net = contrib + saved - 50000
        ev_r += prob * net

    log(f"  EV(Pricing):  £{ev_p:,.0f}")
    log(f"  EV(Referral): £{ev_r:,.0f}")
    log(f"  Ratio: {ev_r/max(ev_p,1):.1f}x")
    log(f"  Winner: {'REFERRAL LOOP' if ev_r > ev_p else 'DYNAMIC PRICING'}")
    return {'ev_pricing': round(ev_p), 'ev_referral': round(ev_r), 'ratio': round(ev_r/max(ev_p,1), 1),
            'winner': 'REFERRAL LOOP' if ev_r > ev_p else 'DYNAMIC PRICING'}


def main():
    args = parse_args()
    out = Path(args.out)
    out.mkdir(exist_ok=True, parents=True)

    def log(m):
        if not args.quiet:
            print(m)

    log(f"Loading {args.input}...")
    clean = load_data(args.input)
    log(f"Clean rows: {len(clean):,}, customers: {clean['Customer_ID'].nunique()}")

    aarrr = compute_aarrr(clean, log)
    cohort_pct, cohort_avg = compute_cohort(clean, log)
    basket = compute_basket(clean, log)
    rfm, seg_summary = compute_rfm(clean, log)
    nash = compute_game_theory(log)
    decision = compute_decision_tree(clean, args.gross_margin, args.cac, log)

    cohort_pct.to_csv(out / 'cohort_retention_matrix.csv')
    basket.to_csv(out / 'basket_rules_top15.csv', index=False)
    rfm.to_csv(out / 'rfm_segments.csv', index=False)
    seg_summary.to_csv(out / 'segment_summary.csv')

    summary = {'aarrr': aarrr, 'cohort': cohort_avg, 'nash': nash, 'decision': decision,
               'mean_ltv': float(clean.groupby('Customer_ID')['Revenue'].sum().mean()),
               'total_revenue': float(clean['Revenue'].sum()),
               'n_customers': int(clean['Customer_ID'].nunique())}
    with open(out / 'run_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    log(f"\nOutputs saved to {out}/")
    return 0


if __name__ == '__main__':
    sys.exit(main())
