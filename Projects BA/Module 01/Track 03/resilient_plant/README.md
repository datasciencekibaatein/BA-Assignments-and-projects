# Resilient Plant · Capital Investment Audit (Track 3)

**Module 1 · Risk & Financial track · Business Analytics**

---

## What this is

A complete financial-risk audit for a $75M capital investment in an automated metals smelter. Six Jupyter notebooks build a sector-calibrated DCF model, a 2-way WACC × Operating-Margin stress test, and a final risk-audit PDF for the capital allocation committee.

Every model input is anchored to the **median of 1,344 Basic Materials company-years (2014–2018)** from the Kaggle 200-Financial-Indicators dataset — no fictional numbers, no extrapolated forecasts.

---

## Folder layout

Place the dataset and notebooks like this:

```
Module 01/
└── Track 03/
    ├── dataset/                                  ← place the 5 yearly CSVs here
    │   ├── 2014_Financial_Data.csv
    │   ├── 2015_Financial_Data.csv
    │   ├── 2016_Financial_Data.csv
    │   ├── 2017_Financial_Data.csv
    │   └── 2018_Financial_Data.csv
    │
    └── resilient_plant/                          ← unzip notebooks here
        ├── 01_metals_peer_benchmark.ipynb
        ├── 02_ratio_analysis_envelope.ipynb
        ├── 03_capital_budgeting_xlsx.ipynb
        ├── 04_stress_test_xlsx.ipynb
        ├── 05_resilience_analysis.ipynb
        └── 06_risk_audit_playbook.ipynb
```

The notebooks auto-detect this layout. `data/`, `outputs/`, and `figures/` will be created automatically inside `resilient_plant/` when you run notebook 01.

---

## Notebook order

| # | Notebook | What it does | Outputs |
|---|---|---|---|
| 01 | `01_metals_peer_benchmark.ipynb` | Loads 5 yearly CSVs, filters to Basic Materials sector, computes clean sector-median ratios (the "calibration anchors" used by every downstream notebook). | `data/metals_cleaned.csv`, `data/calibration_anchors.csv`, `figures/sector_median_trends.png`, `figures/dispersion_envelope.png` |
| 02 | `02_ratio_analysis_envelope.ipynb` | Cross-sectional dispersion analysis. Builds liquidity, solvency, profitability percentile bands (10/25/50/75/90) for each year. | `outputs/volatility_profile.csv`, `outputs/cross_sectional_dispersion.csv`, 3 envelope PNGs |
| 03 | `03_capital_budgeting_xlsx.ipynb` | Builds `Capital_Budgeting_Model.xlsx` — full Y0-Y10 DCF with TVM, NPV, IRR, Profitability Index. CapEx staggered $30M/$25M/$20M Y0-Y2; production Y3-Y10. Includes Python sanity check. | `outputs/Capital_Budgeting_Model.xlsx` |
| 04 | `04_stress_test_xlsx.ipynb` | Builds `Stress_Test_2Way.xlsx` — 9×12 grid showing project NPV at every WACC × Op-Margin combination (8-16% × 5-16%). Conditional formatting green/red. Plus Break-Even contour sheet. | `outputs/Stress_Test_2Way.xlsx` |
| 05 | `05_resilience_analysis.ipynb` | Sector resilience analysis: bottom-quartile-margin "shocked" cohort vs healthy cohort. Recovery profile (which firms bounced back, what their balance sheets looked like). Empirical Danger Zone calibration. | `outputs/shocked_vs_healthy_profile.csv`, `outputs/empirical_stress_frequency.csv`, `outputs/recovery_resilience_profile.csv`, `outputs/project_vs_sector_distribution.csv`, 2 PNGs |
| 06 | `06_risk_audit_playbook.ipynb` | Compiles the **Financial Risk Audit PDF** — the final deliverable for the capital-allocation committee. | `outputs/Financial_Risk_Audit.pdf` |

Run them in order (01 → 06). Notebook 06 depends on outputs from 01-05.

---

## Final deliverables

After running all 6 notebooks, your `outputs/` folder contains:

1. **`Financial_Risk_Audit.pdf`** — the committee-ready audit (8 pages, charts, tables, recommendations)
2. **`Capital_Budgeting_Model.xlsx`** — fully-formula-driven DCF with editable yellow input cells
3. **`Stress_Test_2Way.xlsx`** — the 2-way WACC × Margin grid plus Break-Even sheet
4. Supporting CSVs that feed the PDF (sector medians, percentile bands, resilience profiles)

---

## The audit's central finding

The data shows that **at sector-median operating economics (7.9% op margin), the project does NOT clear the WACC hurdle.** NPV = -$8.6M at base case. The project becomes value-creating only at op margins above ~12% — the top quartile of the metals sector.

This is the honest finding the data supports. The 2-way stress test shows exactly which WACC × Margin combinations turn the project value-creating, and the resilience analysis identifies what balance-sheet ratios distinguish firms that survived metals-sector shocks from those that didn't.

---

## Reframing notes (vs original brief)

To make every task fully data-supported with the Kaggle dataset, two original brief items were reframed:

| Original | Reframed | Why |
|---|---|---|
| 5-year **forecast** of sector ratios | 5-year **cross-sectional dispersion** + percentile bands | 5 data points is too thin for forecasting; dispersion across 1,200+ companies is robust |
| Stress test on **raw material prices** | Stress test on **Operating Margin** | Margin is downstream of raw-material prices and IS in the dataset; raw prices aren't |
| Supply/demand **equilibrium** analysis | Sector **resilience** analysis (shocked vs healthy cohorts, recovery profile) | Equilibrium analysis requires commodity price data not in dataset; resilience analysis answers the same question (what happens under shock?) using only the data available |
| "Probability of distress" | "Empirical percentile" mapping | Probabilities require longer history; percentile mapping is exact for the observed data |

---

## Tech requirements

- Python 3.10+
- `pandas`, `numpy`, `matplotlib`, `seaborn`, `openpyxl`, `reportlab`, `numpy-financial`, `scipy`

Install: `pip install pandas numpy matplotlib seaborn openpyxl reportlab numpy-financial scipy`
