# Power BI Executive Roadmap Spec — PivotCo Product Pivot

> **Tool:** Power BI Desktop (current version) — explicit brief requirement: "A Power BI Executive Roadmap with DAX-calculated 'Churn Probability'".
> **Audience:** Product Manager, CPO, VP Customer Success
> **Purpose:** Real-time visibility into churn risk across the customer base, with drill-through to segment, contract type, and individual customer scores.

---

## 1. Data Sources

Connect Power BI to:

| File | Rows | Purpose |
|---|---|---|
| `outputs/churn_scores.csv` | 7,043 | **Headline source:** customer_id, churn_prob, predicted_churn, segment, tenure, monthly, contract, features_adopted |
| `outputs/dashboard_kpis.csv` | 16 | Headline KPIs strip |
| `outputs/decision_tree_inputs.csv` | 3 | Per-contract LTV / churn rate / lifetime |
| `outputs/feature_importance.csv` | 25 | Top churn drivers (logistic regression coefficients) |
| `outputs/pivotco.db` (SQLite) | — | Single-connection alternative; exposes 6 analytical views |

For a live deployment, replace CSVs with a direct connection to the production data warehouse and refresh nightly.

---

## 2. Data Model (Star Schema)

```
                ┌────────────────────┐
                │  dim_subscriber    │
                │  (7,043 rows)      │
                └─────────┬──────────┘
                          │
                          │ customer_id
                          │
        ┌─────────────────┼─────────────────┐
        │                 ▼                 │
        │     ┌──────────────────────┐     │
        │     │  fact_customer_state │     │
        │     │  (7,043 rows)        │     │
        │     └────┬─────────────┬───┘     │
        │          │             │         │
        │          │             │         │
   ┌────▼────┐ ┌───▼────────┐ ┌──▼──────┐
   │ dim_    │ │ dim_       │ │ dim_    │
   │ contract│ │ payment    │ │ tenure_ │
   │         │ │            │ │ bucket  │
   └─────────┘ └────────────┘ └─────────┘
```

Mark `dim_subscriber.customer_id` as the dimension key. Set relationships as 1:* from each dim to fact.

---

## 3. Core DAX Measures

### 3.1 Headline measures

```dax
// Total customers
Total Customers = COUNTROWS(fact_customer_state)

// Churned customers (actual)
Total Churned =
CALCULATE(
    COUNTROWS(fact_customer_state),
    fact_customer_state[churn_flag] = 1
)

// Actual churn rate (denominator-aware)
Churn Rate =
DIVIDE(
    [Total Churned],
    [Total Customers],
    0
)

// Average predicted churn probability (the headline DAX measure)
Avg Churn Probability =
AVERAGE(churn_scores[churn_prob])

// Predicted churn rate at default threshold (0.5)
Predicted Churn Rate (50%) =
DIVIDE(
    CALCULATE(COUNTROWS(churn_scores), churn_scores[churn_prob] >= 0.5),
    [Total Customers],
    0
)
```

### 3.2 Tunable threshold measures (the brief's required DAX)

```dax
// Threshold parameter (use What-If Parameter, default 0.5)
Churn Threshold = SELECTEDVALUE('Threshold'[Threshold], 0.5)

// Customers flagged as high-risk at the chosen threshold
High Risk Count =
CALCULATE(
    COUNTROWS(churn_scores),
    churn_scores[churn_prob] >= [Churn Threshold]
)

// High Risk % of book
High Risk Pct =
DIVIDE(
    [High Risk Count],
    [Total Customers],
    0
)

// Revenue at risk at the chosen threshold
Revenue At Risk =
CALCULATE(
    SUM(churn_scores[monthly_charges]),
    churn_scores[churn_prob] >= [Churn Threshold]
)

// Annualized revenue at risk (assume churners stay 0 days)
Annualized Revenue At Risk = [Revenue At Risk] * 12
```

### 3.3 Segment / contract slicer-aware measures

```dax
// Selected-segment churn probability average
Segment Avg Churn Prob =
CALCULATE(
    [Avg Churn Probability],
    ALLSELECTED(churn_scores[segment])
)

// Contract-type LTV (uses dim_contract for sorted display)
Avg LTV by Contract =
DIVIDE(
    SUMX(churn_scores, churn_scores[monthly_charges] * churn_scores[tenure_months]),
    [Total Customers],
    0
)

// Contract uplift: 2yr vs MTM LTV ratio
LTV Uplift Ratio =
DIVIDE(
    CALCULATE([Avg LTV by Contract], churn_scores[contract_type] = "Two year"),
    CALCULATE([Avg LTV by Contract], churn_scores[contract_type] = "Month-to-month"),
    0
)
```

### 3.4 Funnel-stage measures

```dax
// Churn rate at the selected tenure bucket
Tenure Cohort Churn Rate =
CALCULATE(
    [Churn Rate],
    USERELATIONSHIP(churn_scores[tenure_bucket], dim_tenure[tenure_bucket])
)

// 0-6mo cliff size (the 53% headline)
Awareness Cliff Pct =
VAR awareness_churners =
    CALCULATE([Total Churned], churn_scores[tenure_bucket] = "0-6mo (Awareness)")
RETURN
    DIVIDE(awareness_churners, [Total Churned], 0)
```

### 3.5 EV decision measures (mirrors Excel Decision_Tree)

```dax
// LTV by contract (computed from data)
LTV MTM =
CALCULATE(
    AVERAGEX(churn_scores, churn_scores[monthly_charges]) * 2.3,
    churn_scores[contract_type] = "Month-to-month"
)

LTV TwoYear =
CALCULATE(
    AVERAGEX(churn_scores, churn_scores[monthly_charges]) * 35.3,
    churn_scores[contract_type] = "Two year"
)

// Skimming EV (parameterized via What-If)
Skimming EV =
VAR conv = SELECTEDVALUE('Conv Rate'[Value], 0.20)
VAR cost = SELECTEDVALUE('Investment Cost'[Value], 200)
RETURN
    conv * ([LTV TwoYear] - [LTV MTM]) - cost

// Penetration EV
Penetration EV =
VAR conv = SELECTEDVALUE('Conv Rate'[Value], 0.30)
VAR cost = SELECTEDVALUE('Investment Cost'[Value], 80)
RETURN
    conv * [LTV MTM] - cost
```

---

## 4. Page-by-Page Layout

### Page 1 — `Executive Overview`

**Layout (1280 × 720):**

```
┌──────────────────────────────────────────────────────────────────┐
│  KPI Strip (full width, 100 px)                                  │
│   Churn Rate | Revenue at Risk | Avg Tenure | Model AUC          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│        ★ Churn Probability Gauge (full width, 200 px) ★          │
│                                                                  │
├──────────────────────────────┬───────────────────────────────────┤
│ Churn % by Tenure Bucket     │ STP Segment Bubble Chart          │
│ (50% × 240 px)               │ (50% × 240 px)                    │
│                              │  size = customer count            │
│                              │  color = churn rate               │
├──────────────────────────────┴───────────────────────────────────┤
│ Decision Tree: Skimming vs Penetration EV                        │
│ (full width, 180 px) — sliders for conversion + cost             │
└──────────────────────────────────────────────────────────────────┘
```

### Page 2 — `Customer Risk Detail`

- **Page filter:** segment slicer + threshold slicer (What-If: 0.0 to 1.0, step 0.05)
- **Customer table** (top 50 highest risk): customer_id, segment, contract, tenure, monthly, churn_prob, predicted_churn flag
- **Drill-down:** click any row → page 3
- **Conditional formatting:** red/amber/green on churn_prob column

### Page 3 — `Customer 360`

- **Page filter:** customer_id (driven by drill-through from Page 2)
- **Cards:** churn_prob, segment, contract, tenure, monthly, features_adopted, lifetime to date
- **Bullet chart:** customer's churn_prob vs segment average vs firm-wide
- **Top contributing factors:** show top 3 features pushing this customer's churn probability up (driven by feature_importance × customer's value)
- **Recommended action:** dynamically generated based on segment + churn_prob:
  - At-Risk High Spender + prob > 0.5 → "Save campaign: 2yr contract incentive + dedicated AM"
  - Low Engagement Newcomer → "Onboarding outreach: schedule feature setup walkthrough"
  - High Value Loyalist → "Maintain: quarterly business review"

### Page 4 — `Strategy Sandbox`

- **What-If sliders:** Conv_Skimming (0–50%), Cost_Skimming ($100–800), Conv_Penetration (0–60%), Cost_Penetration ($50–300)
- **Live KPIs:** EV(Skimming), EV(Penetration), Recommendation cell, 12-month projected impact
- **Sensitivity heatmap:** 2D table just like Excel Sensitivity sheet, but interactive

### Page 5 — `Top Churn Drivers`

- **Source:** `feature_importance.csv`
- **Bar chart:** top 12 features by absolute coefficient, colored by direction (red = increases churn, green = decreases)
- **Annotations:** highlight `tenure` (strongest negative), `Contract_Month-to-month` (strongest positive after Internet)

---

## 5. Page Filters & Slicers

| Slicer | Pages | Type | Default |
|---|---|---|---|
| Segment | 1, 2, 3 | Multi-select | All |
| Contract type | 1, 2, 4 | Multi-select | All |
| Tenure bucket | 1 | Single-select | All |
| Churn threshold | 2 | What-If (0.0–1.0) | 0.5 |
| Conv_Skimming | 4 | What-If (0–0.5) | 0.20 |
| Cost_Skimming | 4 | What-If ($100–$800) | $200 |

---

## 6. Verification Checklist

After publishing:

| Visual | Cell / Value | Expected | ✓ |
|---|---|---|---|
| KPI Strip | Churn Rate | 26.5% | ☐ |
| KPI Strip | Revenue at Risk | $139,131 | ☐ |
| KPI Strip | Model AUC | 0.844 | ☐ |
| Churn by Tenure | 0-6mo cliff | 52.9% | ☐ |
| Churn by Tenure | 49-72mo Advocacy | 9.5% | ☐ |
| STP Bubble | At-Risk High Spenders | n=1,465, churn=52% | ☐ |
| STP Bubble | High Value Loyalists | n=1,419, churn=11% | ☐ |
| Decision Tree | Skimming EV | +$198 | ☐ |
| Decision Tree | Penetration EV | −$34 | ☐ |
| Decision Tree | Recommendation | SKIMMING | ☐ |
| Customer 360 | Top driver: tenure | coef = −0.79 | ☐ |
| Customer 360 | Top driver: Fiber optic | coef = +0.65 | ☐ |

---

## 7. Theme

| Element | Hex | Usage |
|---|---|---|
| Navy | `#1F3864` | Primary; KPI strip; chart backgrounds |
| Green | `#2E7D32` | Retained / capable / positive EV |
| Red | `#C00000` | Churned / at-risk / negative EV |
| Amber | `#E07A1F` | Marginal / warning |
| Gold | `#FFC000` | Highlighted recommendations |
| Light-blue | `#D9E2F3` | Section dividers |

Font: Segoe UI (Power BI default). Titles 14pt bold. KPI numbers 28pt bold.

---

## 8. Methodology Callout (page footer)

> **Methodology.** Churn probability scored via L2-regularized logistic regression on 25 features (numeric + binary + one-hot categoricals). Trained on 75% / tested on 25%, AUC = 0.844. Top features by coefficient: tenure (−0.79, longer = lower risk), Fiber optic Internet (+0.65, higher risk), Contract type (Two-year = −0.30 vs Month-to-month = +0.30). LTV calculations use the geometric expected lifetime: 1/churn_rate × monthly_charges. EV figures use industry-standard SaaS conversion benchmarks (10–30% for tier upgrades, 20–40% for new acquisition). **PivotCo financials are synthetic, anchored to dataset scale; per-customer numbers are real but firm-level revenue ($200M ARR) is narrated for boardroom relevance.**
