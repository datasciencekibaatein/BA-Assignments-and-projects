# Consult-Tech — Workforce Stability & Market Equilibrium (Track 2, Product & Consulting)

Deliverable bundle for the brief: *advise a client on opening a new R&D centre in Bengaluru, India, balancing CPI-inflation risk with employee-attrition stability*.

## What's in the bundle

| File | Purpose |
|---|---|
| `Consult_Tech_Workforce_Analytics.ipynb` | The analytics notebook — runs Power Query equivalent cleanup, pre-computes every DAX measure, runs the CLT analysis, and exports CSV inputs for the Excel model |
| `Market_Feasibility_Model.xlsx` | Excel feasibility model with 7 sheets (Cover, Inputs, Macro_India, Scenarios, Model, Sensitivity, Summary). All 112 formulas validated, zero errors. |
| `PowerBI_Build_Spec.md` | Complete spec for assembling the `.pbix` dashboard: Power Query M code, every DAX measure, 3-page visual layout, slicers, theme JSON. ~45 min build time. |
| `india_macro_indicators.csv` | India CPI inflation + RBI repo rate, 2015-2025 (sourced from World Bank / RBI) |

## Folder layout (when you run it)

```
Module 02/
└── Track 02/
    ├── dataset/
    │   ├── WA_Fn-UseC_-HR-Employee-Attrition.csv     ← from Kaggle
    │   └── india_macro_indicators.csv                ← bundled
    └── consult_tech/
        ├── Consult_Tech_Workforce_Analytics.ipynb    ← run this first
        ├── Market_Feasibility_Model.xlsx             ← already built, open in Excel
        ├── PowerBI_Build_Spec.md                     ← follow to build .pbix
        ├── data/
        ├── outputs/                                  ← notebook writes CSVs here
        └── figures/                                  ← notebook writes PNGs here
```

## Workflow (the recommended order)

### Step 1 — Run the Jupyter notebook

```bash
jupyter notebook Consult_Tech_Workforce_Analytics.ipynb
```

It does five things:

1. Power-Query equivalent cleanup of the IBM HR data (drops 3 degenerate columns, adds 5 derived ones)
2. Pre-computes every DAX measure so you know what each Power BI card should display
3. Runs the **Central Limit Theorem analysis** — sampling distributions for n=30, 50, 100, 200; 90/95/99% confidence intervals on `JobSatisfaction`
4. Generates the macroeconomic scenario inputs that feed the Excel model
5. Exports 11 CSVs and 3 figures to `outputs/` and `figures/`

Run time: ~15 seconds.

### Step 2 — Open the Excel model

`Market_Feasibility_Model.xlsx` opens natively in Excel with all 7 sheets ready. The model has been validated end-to-end (Base Case = ₹18.86M annual cost for 200-headcount, matches notebook prediction).

**To use as Scenario Manager replacement:**

The standard Excel Scenario Manager creates named scenarios that swap input cells. We've gone one better — the **Scenarios** sheet contains all 3 scenarios as columns, and the **Model** sheet picks the active scenario via cell `C14` (1=Best, 2=Base, 3=Stress). Just change that cell to flip between scenarios; the entire Model + Summary recalculates.

If you specifically want to add a native Scenario Manager:
1. Open `Market_Feasibility_Model.xlsx`
2. **Data → What-If Analysis → Scenario Manager**
3. Click **Add**, name it "Best Case", select changing cells `Scenarios!C8:C11`, click OK
4. Repeat for Base and Stress (using D8:D11 and E8:E11)

But this is optional — the column-based design works the same way and is easier for executives to read.

### Step 3 — Build the Power BI dashboard

Open `PowerBI_Build_Spec.md` and follow the steps in order. The spec contains:

- The exact **Power Query M code** (paste into Advanced Editor)
- All **20+ DAX measures** with explanations
- A **3-page visual layout** (Executive Overview, Drill-down, Statistical Foundation)
- A **theme JSON** for consistent branding
- A **verification checklist** (e.g., "Total Employees card shows 1,470" — confirms your DAX is correct)

Build time: ~45 minutes in Power BI Desktop.

## Headline findings (from the data)

- **Total attrition: 16.12%** (237 of 1,470 employees)
- **Highest-risk role: Sales Representative at 39.76%** (33 of 83 left) — primary executive insight
- **OverTime is the biggest behavioural driver: 2.92x multiplier** (30.53% with OT vs 10.44% without)
- **Tenure cohort decay:** 34.88% → 18.43% → 13.07% → 12.28% → 8.13% across tenure buckets — the rolling attrition pattern is dramatic
- **Morale 95% CI:** [2.51, 2.95] from a single n=100 sample, true population mean = 2.73 (within CI ✓)
- **Year-1 cost across 3 macro scenarios:** ₹18.30M (Best) → ₹18.86M (Base) → ₹19.91M (Stress) for 200 headcount

## Methodology notes

The brief uses two terms the IBM HR dataset doesn't directly support. The standard substitutions documented in the spec:

| Brief term | Our proxy | Why |
|---|---|---|
| **"Rolling Attrition Rate"** | Tenure-cohort attrition | IBM data has no hire/termination dates, only `YearsAtCompany`. Standard proxy used in every IBM HR Analytics tutorial. |
| **"Market Structure"** | `BusinessTravel` (3 levels) | IBM data has no market labels. Travel frequency = labour-market exposure (more recruiter contact). |

Both substitutions are flagged explicitly in the Power BI dashboard's methodology callout, so an examiner reads them upfront.

## Dependencies

- Python 3.9+ with: pandas, numpy, scipy, matplotlib, seaborn, openpyxl
- Excel 2016+ or LibreOffice Calc to open the `.xlsx`
- Power BI Desktop (free) to build the `.pbix` from the spec
