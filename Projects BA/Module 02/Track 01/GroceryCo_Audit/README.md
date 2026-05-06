# GroceryCo Operational Integrity & Basket Audit — Track 1 (Analyst)

Six Jupyter notebooks that build a committee-ready operational audit on the Instacart Market Basket dataset. Reframed from the original "Aero-Logistics" brief because the dataset has no Suppliers/Shipments/Costs/lead-times — every brief task has a 1-to-1 mapping onto basket-integrity equivalents.

## Folder layout

Place the notebooks and the dataset like this:

```
Module 01/
└── Track 01/
    ├── dataset/                              ← put the 5 Kaggle CSVs here
    │   ├── aisles.csv
    │   ├── departments.csv
    │   ├── products.csv
    │   ├── orders.csv
    │   └── order_products__train.csv
    └── grocery_audit/                        ← put these 6 notebooks here
        ├── 01_database_design.ipynb
        ├── 02_complex_joins_cascade.ipynb
        ├── 03_skewness_spc_control_charts.ipynb
        ├── 04_hypothesis_tests.ipynb
        ├── 05_tableau_data_prep.ipynb
        └── 06_audit_playbook.ipynb
```

The notebooks auto-resolve paths — they hunt for the `grocery_audit` folder up the directory tree, then look for the dataset in a sibling `dataset/` folder OR a child `data/` folder. Both work.

`outputs/` and `figures/` are created automatically the first time you run.

## Run order

Run the 6 notebooks in numerical order. Each one writes to `outputs/` and `figures/`; the next one reads from there.

| # | Notebook | Builds | Time |
|---|---|---|---|
| 1 | `01_database_design.ipynb` | `outputs/groceryco.db` (SQLite, ~91 MB), ER diagram PNG | ~30s |
| 2 | `02_complex_joins_cascade.ipynb` | Reorder cascade analysis, variance ratio, heatmap | ~10s |
| 3 | `03_skewness_spc_control_charts.ipynb` | SPC stats, X-bar control chart, Western Electric checks | ~15s |
| 4 | `04_hypothesis_tests.ipynb` | Three Welch t-tests + distribution plots | ~5s |
| 5 | `05_tableau_data_prep.ipynb` | `tableau_extract.csv` (~145 MB), summary CSV, dashboard spec | ~30s |
| 6 | `06_audit_playbook.ipynb` | `Operational_Audit_Playbook.pdf` (final deliverable) | ~5s |

Total run time: about 90 seconds end-to-end.

## What you get

In `outputs/`:
- **Operational_Audit_Playbook.pdf** — committee-ready audit, 6 sections (exec summary, ER + schema, cascade, SPC, t-tests, dashboard, recommendations + methodology)
- **groceryco.db** — 3NF SQLite database with 5 tables, FK constraints, indexes
- **tableau_extract.csv** — denormalised flat file for Tableau (1.38M rows × 14 cols)
- **tableau_summary_extract.csv** — pre-aggregated extract for fast prototyping (~441 rows)
- **dashboard_spec.md** — full Tableau workbook spec (sheets, marks, calculated fields, layout)
- Supporting CSVs: `spc_department_stats.csv`, `spc_western_electric.csv`, `ttest_results.csv`, `cascade_slope_by_department.csv`, `variance_per_lead_bucket.csv`

In `figures/`:
- `er_diagram.png`, `cascade_heatmap.png`, `cascade_top5_lines.png`, `control_chart_xbar.png`, `distributions_skewness.png`, `dow_hour_heatmap.png`, `ttest_distributions.png`, `dashboard_mockup.png`

## Brief-to-data task mapping

The original brief asked for a logistics audit. The Instacart dataset has no logistics fields. Every task is preserved in spirit:

| Original brief task | Reframed task | Same skills demonstrated |
|---|---|---|
| ER model: Suppliers → Shipments → Costs | ER model: Departments → Aisles → Products → Orders → Order_items | 1NF→3NF normalization, FK constraints |
| Bullwhip across lead times (SQL joins) | Reorder Cascade Effect across `days_since_prior_order` buckets | Complex 4-table SQL CTEs, variance amplification |
| SPC control charts on logistics hubs | SPC control charts on departments | X-bar charts, peer-band limits, Western Electric rules |
| T-test: Expedited vs Standard shipping | T-test: Weekend vs Weekday + Morning vs Evening | Welch t-test, Cohen's d, 95% CIs, effect sizes |
| Tableau: Operational Health + Margin Leakage | Tableau: Operational Health + Reorder Leakage | Same Tableau skills, same dashboard structure |

## Tableau dashboard

This bundle does **not** include a `.twbx` file (Tableau isn't available in the build environment). What it does include:
1. The CSV/extract Tableau connects to (`tableau_extract.csv`)
2. A complete spec for the workbook (`dashboard_spec.md`) — sheets, marks, calculated fields, layout
3. A matplotlib mockup showing what the live dashboard will look like (`figures/dashboard_mockup.png`)

Building the actual `.twbx` from the spec takes ~30 minutes in Tableau Desktop or Tableau Public.

## Methodology notes

- **Train-only.** We use only `order_products__train.csv` (1.38M line items, 131K orders), not `prior` (32M rows). The train set provides more than enough statistical power for n-of-thousands t-tests and 21-department control charts; adding `prior` would not change conclusions.
- **Welch t-test** (not Student's). Variances are unequal between segments. Welch is more conservative and the right default. Sample sizes (24K-85K) ensure CLT robustness against right-skew.
- **SPC framing.** Peer-comparison X-bar with cross-department spread as the noise floor: ±2σ for OUT, ±1σ for WARN. Departments are treated as peer observations in a 21-department operational system.
- **Findings are real.** Every number in the PDF is computed from the actual data — no synthetic numbers, no extrapolations.

## Dependencies

```
pandas
numpy
scipy
matplotlib
seaborn
reportlab
```

All standard. No API keys, no external services.
