# Zero-Defect Initiative — Marketplace Operations Audit

**Track 1 (Analyst) deliverable.** Statistical Process Control audit of order-to-delivery lead times for a Brazilian marketplace operator (Olist anchor data: 95,082 delivered orders across 27 states and 3,095 sellers, 2017-01 to 2018-08).

---

## Files in this bundle

| File | Contents |
|---|---|
| `ZeroDefect_Audit.ipynb` | End-to-end Python notebook: SQL extract → SPC charts → hypothesis tests → SARIMA forecast → Tableau exports |
| `ZeroDefect_Audit_Engine.xlsx` | 8-sheet financial model: state SLA reset + seller intervention scenarios, margin-loss bridge, capacity forecast (153 formulas, validated zero errors) |
| `Tableau_Dashboard_Spec.md` | Build instructions for the Operational Control dashboard (~40 min build) |
| `Fishbone_5Whys.md` | BPMN swimlane + 4 OOC patterns × (5-Whys + Ishikawa diagram) |
| `sql/schema.sql` | 3NF schema: 8 base tables + 6 analytical views |
| `sql/load_data.py` | Olist CSV → SQLite loader |
| `README.md` | This file |

---

## Folder layout (for running the notebook)

```
Module 02/
└── Track 01/
    └── zerodefect_audit/
        ├── ZeroDefect_Audit.ipynb      <- this notebook
        ├── ZeroDefect_Audit_Engine.xlsx
        ├── Tableau_Dashboard_Spec.md
        ├── Fishbone_5Whys.md
        ├── README.md
        ├── sql/
        │   ├── schema.sql
        │   └── load_data.py
        ├── data/                        <- place 8 Olist CSVs here
        ├── outputs/                     <- DB and tableau CSVs land here
        └── figures/                     <- notebook PNGs land here
```

The notebook auto-resolves paths by searching for the `zerodefect_audit` folder in its parent chain.

---

## Workflow

1. **Download the Olist data** (from Kaggle or wherever you got it) into `data/`. Required tables:
   - `olist_orders_dataset.csv`
   - `olist_customers_dataset.csv`
   - `olist_sellers_dataset.csv`
   - `olist_products_dataset.csv`
   - `olist_order_items_dataset.csv`
   - `olist_order_payments_dataset.csv`
   - `olist_order_reviews_dataset.csv`
   - `product_category_name_translation.csv`

2. **Build the SQLite database** (one-time, ~30s):
   ```bash
   python sql/load_data.py
   ```
   Produces `outputs/olist_audit.db` (~115 MB).

3. **Run the notebook**: `ZeroDefect_Audit.ipynb`. This builds figures into `figures/` and Tableau-ready CSVs into `outputs/`.

4. **Open the Excel engine**: edit blue/yellow cells; toggle scenario picker (Scenarios sheet, cell C12).

5. **Build the Tableau dashboard** following `Tableau_Dashboard_Spec.md`.

6. **Read `Fishbone_5Whys.md`** for the BPMN swimlanes and root-cause documentation.

---

## Headline findings

| Finding | Evidence | Implication |
|---|---|---|
| **Standard SPC fails on this data** | Lead-time skew = +3.83. Naive Shewhart I-MR gives LCL = −1.2 days (impossible) | First-order audit insight: the corrected method is log-transformed I-MR + daily p-chart |
| **Geography dominates variance** | São Paulo: 8.8d mean. Roraima: 29.9d mean. Kruskal-Wallis p < 1e-30 | Differentiated SLA promises by state (vs current uniform 24-day promise) |
| **5× variation across high-volume sellers** | Late-rate range 5%-24% among 202 sellers with 100+ orders | Bottom decile (~20 sellers) is intervention target |
| **Approval queue tail** | Median 0.3h, mean 9.6h, P95 45.8h, skew 4.45 | Marketplace-side bottleneck; needs queue SLA |
| **Margin Preservation = review collapse** | On-time → 4.29 stars; Late 8+d → **1.73 stars** with 76% in 1-2 star range | Lateness is the #1 driver of returns; #1 margin leak |
| **Capacity forecast usable** | SARIMA(1,1,1)x(1,1,1,7) holdout MAPE = 18.1% | 60-day forward forecast supports rolling capacity decisions |

---

## Methodology notes

- **SPC charts.** Three side-by-side: raw I-MR (to demonstrate the false-alarm problem), log-transformed I-MR (the corrected version), daily p-chart on % late (for ongoing operational monitoring). Standard 3σ control limits using d2 constants for individuals charts.
- **Hypothesis testing.** Kruskal-Wallis (non-parametric ANOVA) for state-level differences — chosen over standard ANOVA because of the strong skew. Significance overwhelming (p < 1e-30 across top 15 states).
- **SARIMA model selection.** SARIMAX(1,1,1)×(1,1,1,7) with weekly seasonality, fitted on 2017-01-01 through 2018-07-22, holdout 2018-07-23 through 2018-08-22. Black Friday 2017 week (Nov 22-28) handled as binary exogenous regressor. Annual seasonality not fitted because the dataset only spans ~22 months — insufficient for stable annual SARIMA components.
- **Data trimming.** Last 7 days of the dataset (2018-08-23 through 2018-08-29) excluded from training and test windows because daily order count drops from ~250 to <70 — this is data truncation in the Olist export, not real volume decline.
- **Margin model.** Late delivery → negative review (1-2 stars) → return request → refund + R$35 shipping penalty. Return-conversion rate (% of negative reviewers who actually return) is a yellow input cell — modify based on your category mix.

---

## Recommendations to operations leadership

1. **SLA Reset (free, R$184K savings/period).** Restate delivery promise differently by region. São Paulo can promise 8-10 days; Northern states should promise 28-30 days. Current uniform 24-day promise systematically over-promises in N. states (driving the 3.5% late-by-8+d band) and over-buffers in São Paulo (wasted goodwill).

2. **Bottom-decile seller intervention (R$10K cost, R$105K savings = 10× ROI).** Mandatory dispatch SLA (carrier handoff within 2 days of approval). One-time training/process review for the worst ~20 sellers.

3. **Combined intervention recovers ~85% of preventable margin loss** (R$197K savings out of R$230K late-only cost).

4. **Approval queue tail.** Add SLA on the manual-review queue itself (4-hour max). Surface review-score collapse as a downstream KPI on the anti-fraud team's dashboard.

5. **Quarterly forecast share with carriers.** The Black Friday 2017 lead-time spike was preventable — carriers were sized for steady-state. SARIMA forecast gives 60-day forward visibility; share with carrier partners as a binding capacity contract.

---

## Honest call-outs

- Anchor dataset is Brazilian e-commerce; the brief's "tech hardware manufacturer" framing was reframed as "marketplace operator audit." All methods transfer. Currency is BRL throughout; convert at ~5.5 BRL/USD if USD reporting needed.
- The R$197K combined savings is a single-period figure. Annualized assuming the audit window represents one period and similar ratios persist year-over-year.
- The 0.30 return conversion rate (% of negative reviewers who actually request a return) is an industry-typical assumption, not a measured number from the data — Olist's CSV does not include return events directly. This input is yellow-flagged in the Excel engine for sensitivity analysis.
- SARIMA model is single-step (no rolling refit shown). For production deployment, refit weekly as new data arrives.
