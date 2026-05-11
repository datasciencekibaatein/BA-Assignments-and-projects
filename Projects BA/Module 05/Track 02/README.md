# Product Pivot — PivotCo SaaS Lifecycle Optimization

**Track 2 v3 — Product & Consulting**
*Data-driven lifecycle optimization for a B2B subscription-services provider*

---

## TL;DR

PivotCo (a synthetic anchor; per-customer numbers from IBM Telco Churn — 7,043 real customer records) loses **26.5% of subscribers annually**, with **$139K/month at-risk revenue**. Month-to-month subscribers churn at **42.7% with 2.3-month lifetime**; two-year subscribers churn at **2.8% with 35.3-month lifetime** (15× LTV difference).

A logistic-regression churn model (AUC=0.844) plus a Decision Tree EV analysis shows **Skimming dominates Penetration by 4×** (+$198 vs −$34 per customer). The recommended pivot: lock customers into multi-year contracts, save the At-Risk High Spenders segment first, close the "1-feature trap" via 30/60/90 onboarding redesign. Projected 12-month impact: **$970K**.

---

## Files in this bundle

| File | Purpose |
|---|---|
| `ProductPivot_Lifecycle.ipynb` | Jupyter notebook — end-to-end analysis (5 tasks, 7 figures, executes clean to ~750KB) |
| `ChurnPlaybook.xlsx` | Excel decision tool — 8 sheets, 62 live formulas, Decision Tree EV + Sensitivity |
| `churn_scorer.py` | Python CLI — batch churn-probability scoring (logistic regression, AUC=0.844) |
| `Power_BI_Roadmap_Spec.md` | Power BI build spec — 5 pages, full DAX measure library, verification checklist |
| `Strategic_Growth_Recommendation.md` | 12-slide Pyramid deck outline (boardroom-ready) |
| `Project_Brief_Reframed.md` | Reframed brief with full diff vs original |
| `sql/schema.sql` | SQLite star schema (3 dims + 1 fact + 6 analytical views) |
| `sql/load_data.py` | Python loader (CSV → SQLite) |
| `data/WA_Fn-UseC_-Telco-Customer-Churn.csv` | Source data (IBM Telco, 7,043 customers × 21 cols, CC license) |
| `README.md` | This file |

---

## Folder layout

```
Module 02/Track 02/product_pivot/
├── README.md
├── Project_Brief_Reframed.md
├── Strategic_Growth_Recommendation.md
├── Power_BI_Roadmap_Spec.md
├── ProductPivot_Lifecycle.ipynb
├── ChurnPlaybook.xlsx
├── data/
│   └── WA_Fn-UseC_-Telco-Customer-Churn.csv
├── sql/
│   ├── schema.sql
│   └── load_data.py
├── scripts/
│   └── churn_scorer.py
├── outputs/        (generated)
│   ├── pivotco.db
│   ├── churn_scores.csv
│   ├── dashboard_kpis.csv
│   ├── decision_tree_inputs.csv
│   ├── feature_importance.csv
│   └── model_diagnostics.txt
└── figures/        (generated)
    ├── task1_funnel.png
    ├── task2_mece.png
    ├── task2_stp.png
    ├── task3_decision_tree.png
    ├── task3_sensitivity.png
    ├── task4_7ps.png
    └── task5_feature_importance.png
```

---

## Workflow

### Option A — Full notebook walkthrough (analyst path)

```bash
# 1. Build the SQLite database from the CSV
cd "Module 02/Track 02/product_pivot"
python sql/load_data.py

# 2. Open and execute the notebook
jupyter notebook ProductPivot_Lifecycle.ipynb
# Run all cells. Generates 7 PNGs in figures/, churn_scores.csv + dashboard_kpis.csv in outputs/

# 3. Open the Excel decision tool
open ChurnPlaybook.xlsx
# Adjust Inputs sheet → Decision_Tree and Sensitivity recalculate live

# 4. Build Power BI dashboard following the spec
# Power_BI_Roadmap_Spec.md walks through 5 pages, all DAX measures, verification checklist

# 5. Present using the deck outline
# Strategic_Growth_Recommendation.md = 12-slide Pyramid structure, boardroom-ready
```

### Option B — Standalone churn scoring (CSM / production path)

```bash
# Score any customer CSV (must have the same 19 input columns as the IBM Telco source)
python scripts/churn_scorer.py \
    --input data/WA_Fn-UseC_-Telco-Customer-Churn.csv \
    --out outputs/

# Outputs:
#   outputs/churn_scores.csv         -- per-customer churn probability + segment + predicted churn flag
#   outputs/feature_importance.csv   -- ranked logistic regression coefficients
#   outputs/model_diagnostics.txt    -- AUC, confusion matrix, top features
```

---

## Headline findings

| # | Finding | Number |
|---|---|---|
| 1 | Firm-wide annual churn rate | **26.5%** |
| 2 | Month-to-month churn rate | 42.7% (LTV $155, expected lifetime 2.3mo) |
| 3 | Two-year churn rate | 2.8% (LTV $2,145, expected lifetime 35.3mo) |
| 4 | LTV uplift: 2-year vs MTM | **15× longer customer lifetime** |
| 5 | First 6 months absorb % of all churn | 53% (the activation cliff) |
| 6 | The "1-feature trap" | 1 feature: **45.8% churn** vs 0 features: 21.4% |
| 7 | Worst payment combo | Electronic check + Paperless = **49.8% churn** |
| 8 | At-Risk High Spenders segment | 1,465 customers, $93/mo, **52% churn** |
| 9 | Monthly revenue at risk | **$139,131** ($1.67M annualized) |
| 10 | Logistic regression model AUC | **0.844** (well-calibrated by segment) |
| 11 | EV(Skimming) per customer | **+$198** |
| 12 | EV(Penetration) per customer | **−$34** |
| 13 | 12-month projected impact | **$970K** |

---

## Methodology

### Logistic regression churn model

- **Features (25 total):** 4 numeric (`tenure`, `MonthlyCharges`, `SeniorCitizen`, `features_adopted`) + 11 binary service flags + 10 one-hot categorical (Contract × Internet × Payment)
- **Train/test split:** 75% / 25%, stratified on churn flag, random_state=42
- **Preprocessing:** StandardScaler fit on train; applied to test and to the full population for scoring
- **Model:** L2-regularized logistic regression (C=1.0, max_iter=1000)
- **Metrics:** AUC=0.844, accuracy=0.80, precision (churn class)=0.65, recall=0.55
- **Top coefficients:** tenure (−0.79, longer = lower risk), MonthlyCharges (−0.74), Internet=No (−0.69), Internet=Fiber optic (+0.65), Contract=Two year (−0.30), Contract=MTM (+0.30)
- **Calibration:** predicted churn rate per STP segment matches actual churn rate within ±2pp across all 5 segments

### LTV calculation

`expected_lifetime_months = 1 / churn_rate` (geometric distribution assumption)
`expected_LTV = monthly_charges × expected_lifetime_months`

This is the standard subscription-LTV formula. It assumes constant monthly churn probability — a good first approximation but understates LTV for customers who pass the 6-month cliff (real survival curves are concave).

### Decision Tree EV

Per-customer EV per strategy:
- **Skimming**: `EV = p_conv × (LTV_2yr − LTV_MTM) − cost_skim` = 20% × ($2,145 − $155) − $200 = **+$198**
- **Penetration**: `EV = p_acquire × LTV_MTM − cost_pen` = 30% × $155 − $80 = **−$34**

Sensitivity grid (in `ChurnPlaybook.xlsx` → Sensitivity sheet) confirms Skimming dominates across the realistic parameter range (10–30% conversion × $100–$500 cost).

### STP Segmentation

Rule-based segmentation on tenure × monthly_charges × contract × features_adopted (no clustering algorithm — these segments are defined to be actionable and interpretable, not statistically optimal). Implemented identically in:
- SQL: `v_stp_segments` view in `sql/schema.sql`
- Python: `assign_segment()` function in both notebook and `churn_scorer.py`

### MECE branches

Five orthogonal axes of churn risk, each with quantified spread:
1. Contract Friction (39.9pp)
2. Service Quality / Internet (34.5pp)
3. Payment Friction (30.1pp)
4. Feature Engagement Gap (40.5pp)
5. Demographic Risk / Senior+Contract (51.9pp)

---

## Honest call-outs

These are deliberate disclosures the user should know before defending the deliverable:

- **PivotCo is a synthetic anchor.** Per-customer numbers (churn rates, LTVs, segment sizes) are real (7,043 actual records from IBM's published dataset). The firm-level $200M ARR and "B2B subscription-services" framing are scaled and narrated for boardroom credibility.

- **Dataset is technically telecom**, not pure SaaS. Subscription mechanics are identical (recurring billing, contract tenure, feature add-ons, churn behavior), but anyone who recognizes the IBM dataset will see the swap. We disclose it on slide 11 of the deck and in the brief reframe document.

- **Skimming/Penetration in the original brief refers to pricing strategy.** We reframe as **contract-strategy** (lock-in vs. volume play) because the dataset has fixed per-service pricing. The EV-tradeoff structure and decision-tree logic are preserved exactly; only the labels move.

- **TotalCharges has 11 blank rows** — all tenure=0 customers (signed up but never billed). Coerced to NaN. Documented in `sql/load_data.py`.

- **Conversion rates ($200 cost @ 20% Skimming, $80 CAC @ 30% Penetration) are industry benchmarks**, not PivotCo-specific. A reviewer should pressure-test these against the company's actual contract-upgrade and acquisition data before signing the budget.

- **The "1-feature trap" finding is observational, not causal.** Customers who adopt exactly 1 feature may be a self-selecting group (lower engagement to begin with). A randomized A/B test on the proposed 30/60/90 onboarding intervention is recommended before full rollout.

- **AUC=0.844 means ~20% of high-risk-flagged customers won't actually churn (false positives).** Save-campaign budgets should account for this; cost per saved customer = (touch cost × precision)⁻¹.

- **Fiber optic anomaly** (42% churn despite premium pricing) is flagged but unexplained by the data. Likely an SLA/expectation mismatch worth a separate root-cause investigation; we surface the finding without overclaiming.

---

## Continuity vs Track 2 v1 (Workforce) and v2 (PremiumPivot)

This is the third Track 2 build. The deliberate choice across versions: each takes a fundamentally different "what does the data tell us about people-and-money decisions?" lens.

| Aspect | v1 — Workforce | v2 — PremiumPivot | **v3 — Product Pivot (this)** |
|---|---|---|---|
| Framework | HR attrition | Pricing elasticity / GMV | SaaS lifecycle / churn / EV |
| Hero metric | OT Odds Ratio = 1.88, AUC = 0.748 | Elasticity = −0.106, $204.6M GMV | LTV uplift = 15×, AUC=0.844 |
| Dataset | IBM HR (real attrition) | Google Play (real apps) | IBM Telco Churn (real subs) |
| Methodology | Logistic regression + OT scenarios | Demand elasticity + GMV simulation | Decision Tree EV + MECE + STP + 7Ps |
| Deliverable | Workforce strategy | GMV optimization model | Power BI roadmap + DAX churn prob |
| Audience | CHRO | Pricing/Product VP | Product Manager / CPO |
| Decision lens | Retention of *employees* | Pricing power on *digital products* | Retention of *customers* |

All three versions share the analytical discipline (cleanroom data audit → quantified hero numbers → MECE decomposition → boardroom-ready deck), but the questions they answer are orthogonal. A reviewer comparing them should see consistency of method, not repetition of finding.

---

## Reproducing the bundle

1. Unzip `ProductPivot_Track2v3_Bundle.zip` into a working folder
2. `cd` into it; the folder will be named `product_pivot/`
3. `pip install pandas numpy matplotlib seaborn scikit-learn openpyxl jupyter` (if not already)
4. Run `python sql/load_data.py` (creates `outputs/pivotco.db`)
5. `jupyter notebook ProductPivot_Lifecycle.ipynb` and Run All
6. Open `ChurnPlaybook.xlsx` and try changing values on the `Inputs` sheet — `Decision_Tree` and `Sensitivity` recalculate live
7. Optionally run `python scripts/churn_scorer.py --input data/WA_Fn-UseC_-Telco-Customer-Churn.csv --out outputs/` to verify the standalone CLI

All hero numbers should match this README and the figures should regenerate identically (random seeds locked at 42).
