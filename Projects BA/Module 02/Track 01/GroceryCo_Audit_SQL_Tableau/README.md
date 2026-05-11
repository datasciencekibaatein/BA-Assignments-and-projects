# GroceryCo Operational Health Audit — Deliverables

End-to-end pipeline: SQLite database → SQL transformation → 4 CSVs → Tableau dashboard.

```
groceryco_audit/
├── README.md                                     ← this file
├── sql/
│   ├── groceryco_dashboard_transform.sql         ← main transformation (creates 4 tables)
│   └── groceryco_export_csvs.sql                 ← exports those tables to CSVs
├── outputs/
│   ├── spc_weekly.csv                            ← SPC control chart data
│   ├── leakage_report.csv                        ← Reorder Leakage Report
│   ├── aisle_drilldown.csv                       ← Aisle-level drill-down
│   └── dashboard_extract.csv                     ← Wide flat table for Tableau
└── specs/
    └── tableau_dashboard_spec.md                 ← Build instructions
```

## How to run

**Prereq:** `outputs/groceryco.db` from Notebook 01 (the SQLite database with departments, aisles, products, orders, order_items already loaded).

```bash
# Step 1 — run the transformation (creates 4 tables inside the DB)
sqlite3 outputs/groceryco.db < sql/groceryco_dashboard_transform.sql

# Step 2 — export to CSVs (run from the directory you want the CSVs dropped in)
cd outputs/
sqlite3 groceryco.db < ../sql/groceryco_export_csvs.sql

# Step 3 — open Tableau, connect to dashboard_extract.csv, follow specs/tableau_dashboard_spec.md
```

That's it. ~30 seconds for steps 1–2; ~30–45 minutes for the Tableau build.

## What the transformation does

1. **Order spine** — engineers `week_id` (synthetic; chunks each user's order_number into 4-order blocks since the dataset has no calendar dates), `is_weekend`, `time_window`.
2. **Department-week subgroups** — for each `(department, week)`, computes mean reorder rate, range, count. Drops sparse weeks (n<50) so SPC chart isn't noisy.
3. **Platform control limits** — Shewhart 3σ p-chart limits using SUM(reordered) / SUM(items) as p̄ and avg subgroup size for σ. Also UWL/LWL at 2σ.
4. **SPC weekly observations** — every (dept, week) row gets ucl/lcl/uwl/lwl/sigma_hat/z_score/spc_status fields appended via CROSS JOIN. This is what the SPC chart plots.
5. **Leakage Report** — per-department rollup with one-sample t-statistic (dept_mean vs platform_mean), approximate two-tailed p-value (Abramowitz–Stegun normal approx since n_weeks is large), and a `leakage_flag` of `LEAKAGE_CONFIRMED` / `LEAKAGE_SUSPECTED` / `OVERPERFORMER` / `STABLE`.
6. **Aisle drill-down** — bottom-5 leaky departments only, broken down by aisle. Used in the dashboard action when you click a department in the Leakage Report.
7. **Dashboard extract** — denormalized wide table joining 4 + 5 above. Single connection in Tableau covers SPC chart + Leakage Report. The aisle drill-down is a separate small CSV (different grain, can't sensibly join).

## Verified on synthetic data

The pipeline was tested on a synthetic 5K-order, 21-department, 200-product database that intentionally planted 3 departments at 30% reorder rate (vs platform 60%) to verify the audit signal lands.

Result: all 3 planted "leaky" departments correctly flagged `LEAKAGE_CONFIRMED`, with all 7 weeks below LCL and t-statistics of −19 to −50 (p ≈ 0). 2 departments deliberately set high (85% reorder) flagged `OVERPERFORMER`. Other 16 flagged `STABLE`.

## Honest call-outs

- **Synthetic week_id**: the Instacart dataset has `order_dow` and `order_hour_of_day` but no calendar dates, so true weekly time-series isn't possible. We use 4-order chunks per user as an analogue. This is a stable subgroup for SPC purposes but is NOT real calendar weeks.
- **p-value approximation** in `leakage_report.csv` uses the A&S normal approximation (good for n_weeks ≥ 30, which we always have). For exact Welch's t-test values use the Notebook 04 output `ttest_results.csv` — those are the values to cite in the audit report.
- **p-chart vs X-bar chart**: since `reordered` is binary 0/1, the proper SPC variant is the **p-chart** (proportion defective). We've used p-chart limits (`σ = √(p(1-p)/n)`) which is mathematically correct here, even though we labeled the field `reorder_rate`. An X-bar/R chart on continuous data (e.g., basket size) is also possible but isn't what the brief asks for.
- **Subgroup size threshold**: weeks with <50 items per (dept, week) are dropped to keep limits stable. With production data this affects only the long-tail "missing" / "other" departments in their early weeks.
