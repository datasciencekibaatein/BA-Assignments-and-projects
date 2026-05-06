# Tableau Dashboard Build Spec — Workforce Risk Audit

This dashboard turns the analytics notebook outputs into an interactive HR/CFO view. Build time in Tableau Desktop or Tableau Public is approximately 35 minutes.

---

## 0. Files you need

All produced by the analytics notebook in `outputs/`:

| File | Use |
|---|---|
| `tableau_employee_master.csv` | **Primary data source** — 1,470 employees with full hierarchy (Department → JobRole → JobLevel → Employee), plus derived risk buckets and tenure/age/distance/income bands |
| `attrition_by_role.csv` | Pre-aggregated role-level summary for the heatmap |
| `dupont_by_role.csv` | Compensation DuPont table |
| `attrition_cost_forecast.csv` | 12 rows: 3 scenarios × 4 years |
| `logistic_regression_coefs.csv` | Coefficients for the "what drives attrition" bar chart |
| `dashboard_kpis.csv` | Headline KPIs |

---

## 1. Connect Data Sources

**Open Tableau Desktop → Connect → Text File**

Connect each CSV in turn. Tableau auto-detects column types. Set each source to **Live** so the dashboard refreshes when the notebook regenerates.

No data-source relationships needed — each chart uses one CSV. The drill-through hierarchy lives inside `tableau_employee_master.csv` and is built using Tableau's native Hierarchy feature.

---

## 2. Calculated Fields & Hierarchy (in `tableau_employee_master`)

### 2.1 Calculated fields

```
[Attrition Numeric]   = IF [Attrition] = "Yes" THEN 1 ELSE 0 END
[Attrition Rate]      = AVG([Attrition Numeric])
[Annual Salary]       = AVG([Monthly Income]) * 12
[Replacement Cost]    = AVG([Annual Salary]) * 1.5
[OT Risk Flag]        = IF [Over Time] = "Yes" AND [Job Level] <= 2
                         THEN "High Risk" ELSE "Standard" END
[Pay Quartile]        = IF [Monthly Income] < 3000 THEN "Q1 (<$3K)"
                         ELSEIF [Monthly Income] < 5000 THEN "Q2 ($3-5K)"
                         ELSEIF [Monthly Income] < 8000 THEN "Q3 ($5-8K)"
                         ELSE "Q4 ($8K+)" END
[Tenure Risk]         = IF [Years At Company] < 2 THEN "Critical (<2yr)"
                         ELSEIF [Years At Company] < 5 THEN "Watch (2-5yr)"
                         ELSE "Stable (5yr+)" END
```

### 2.2 The drill-through hierarchy

In the Data pane, drag dimensions onto each other to create:

```
Workforce Hierarchy
├── Department         (top: 3)
├── Job Role           (9)
├── Job Level          (5)
└── Employee Number    (row-level: 1,470)
```

---

## 3. Build the Sheets

### Sheet 1 — Executive KPI Strip

- **Source:** `dashboard_kpis`
- **Visual:** 5 large-number KPI tiles in a row
- **Tiles:** Total Headcount | Overall Attrition Rate (red if >15%) | Median Income | Median Tenure | % on Overtime
- **Format:** Large bold numbers, muted captions

### Sheet 2 — Attrition Heatmap (Department × JobRole)

- **Source:** `tableau_employee_master`
- **Visual:** Highlight table
- **Rows:** `Department`, then `Job Role` (drill-through enabled)
- **Color:** `Attrition Rate`, diverging green→yellow→red
- **Label:** Attrition rate as percentage, headcount in smaller font below
- **Title:** "Attrition Rate by Department × Role"

### Sheet 3 — Compensation DuPont Stacked Bar

- **Source:** `dupont_by_role`
- **Visual:** Horizontal stacked bar
- **Rows:** `JobRole`
- **Columns:** Three computed components — Pay (annual), Retention loss (pay × (1/retention - 1)), Tenure loss
- **Color:** Three colors (navy / orange / red)
- **Label:** Total cost-per-retained-FTE on the right edge
- **Sort:** Descending by total cost
- **Title:** "Compensation DuPont — Cost per Retained FTE by Role"

### Sheet 4 — Logistic Regression Drivers

- **Source:** `logistic_regression_coefs`
- **Visual:** Horizontal bar chart (signed)
- **Rows:** `Variable`, sorted by absolute coefficient
- **Columns:** `Coef Std`
- **Color:** Red if positive (increases attrition), green if negative
- **Reference line:** X = 0
- **Title:** "What actually drives attrition? (Standardised Logistic Regression Coefficients)"
- **Annotation:** "AUC = 0.748 (out-of-sample)"

### Sheet 5 — 3-Scenario Cost Forecast

- **Source:** `attrition_cost_forecast`
- **Visual:** Line chart with markers
- **Columns:** `Year`
- **Rows:** `Total Cost` (in $M)
- **Color:** `Scenario` (Baseline = navy, Wage-Inflation = red, Retention-Investment = green)
- **Marker:** Different shape per scenario
- **Annotation:** Cumulative-savings callout: "Wage-Inflation costs +$19M cumulatively vs Baseline"

### Sheet 6 — Distance vs Pay Scatter (the brief's framing question)

- **Source:** `tableau_employee_master`
- **Visual:** Scatter plot
- **Columns:** `Distance From Home`
- **Rows:** `Monthly Income`
- **Color:** `Attrition` (Yes = red, No = grey, opacity 0.5)
- **Reference lines:** Median Distance, Median Income
- **Title:** "Distance vs Pay vs Attrition — visual answer to the brief's question"
- **Caption:** "Distance and Pay both correlate weakly with attrition; OverTime is the strongest driver."

### Sheet 7 — OverTime × JobLevel Crosstab (the audit's hero finding)

- **Source:** `tableau_employee_master`
- **Visual:** Highlight table
- **Rows:** `Over Time`
- **Columns:** `Job Level`
- **Color:** `Attrition Rate`, red→green inverted
- **Label:** Attrition rate (%) and headcount
- **Title:** "Attrition Rate: OverTime × Job Level — the bleeding wound is OT × JL1"

### Sheet 8 — Drill-Through Detail Table

- **Source:** `tableau_employee_master`
- **Visual:** Detail table
- **Rows:** `Employee Number`, `Department`, `Job Role`, `Job Level`, `Monthly Income`, `Distance From Home`, `Over Time`, `Years At Company`, `Attrition`
- **Filter:** **Filtered by every other sheet** via Dashboard Actions
- **Sort:** Attrition (Yes first), then Years At Company ascending

---

## 4. Assemble the Dashboard

**File → Dashboard → New Dashboard**, size = 1440 × 900.

Layout:

```
+-----------------------------------------------------------------------+
| TITLE: Workforce Risk Audit — IBM HR Analytics                        |
+-----------------------------------------------------------------------+
| Sheet 1: 5 KPI tiles                                                  |
+-----------------------------+----------------------------------------+
| Sheet 2: Attrition Heatmap  | Sheet 4: Logistic Regression Drivers   |
+-----------------------------+----------------------------------------+
| Sheet 3: DuPont Stacked Bar | Sheet 7: OverTime × JobLevel Crosstab  |
+-----------------------------+----------------------------------------+
| Sheet 5: 3-Scenario Forecast| Sheet 6: Distance vs Pay Scatter       |
+-----------------------------+----------------------------------------+
| Sheet 8: Drill-Through Detail Table                                   |
+-----------------------------------------------------------------------+
| Filters: [Department] [Job Level] [OverTime] [Tenure Band]            |
+-----------------------------------------------------------------------+
```

---

## 5. Dashboard Actions — The Drill-Through

### Action 1: "Filter to Detail" (Filter)
- **Source:** Sheets 2, 3, 7
- **Target:** Sheet 8
- **Run on:** Select
- **Source fields:** `Department`, `Job Role`, `Job Level`, `Over Time`
- **Behavior:** Clicking any cell filters the detail table

### Action 2: "Highlight related" (Highlight)
- **Source:** All
- **Target:** All
- **Run on:** Hover
- **Source field:** `Job Role`

### Action 3: "Reset View" (Button)
- Standard reset button for one-click clear

---

## 6. Verification Checklist

Before publishing, verify these numbers match the notebook:

- [ ] **Sheet 1:** Total headcount = **1,470**, Attrition = **16.12%**
- [ ] **Sheet 2:** Sales Rep cell = **39.8% attrition** (highest); Research Director = **2.5%** (lowest)
- [ ] **Sheet 3:** Sales Rep total cost-per-retained = **~$128K** (the highest bar)
- [ ] **Sheet 4:** Largest positive bar = **OverTime**; largest negative bars = **Age** and **JobLevel**
- [ ] **Sheet 5:** Year-3 Wage-Inflation ≈ **$30M**; Baseline ≈ $24M; Retention ≈ $23M
- [ ] **Sheet 7:** OverTime=Yes × JobLevel=1 cell shows the highest attrition rate

---

## 7. Theme

| Element | Color |
|---|---|
| Title bar | Navy `#1F3864` |
| KPI good values | Green `#2E7D32` |
| KPI critical values | Red `#C00000` |
| Baseline scenario | Navy `#1F3864` |
| Wage-Inflation scenario | Red `#C00000` |
| Retention-Investment scenario | Green `#2E7D32` |
| Background | White |
| Body text | `#333333` |
| Font | Calibri / Tableau default |

---

## Appendix — Methodology callout

Add as a text caption on the dashboard:

> **Methodology.** Source: IBM HR Analytics Employee Attrition (Kaggle), 1,470 employees. Logistic regression with multicollinearity check (VIF). Compensation DuPont = Annual Pay × (1/Retention) × (1/Tenure Multiplier). Cost forecast: Departures × Salary × 1.5 replacement multiplier, compounded with wage inflation. AUC = 0.748 (holdout).
