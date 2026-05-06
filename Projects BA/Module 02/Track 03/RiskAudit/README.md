# Track 3 — Project Risk Audit

**Capital Deployment & Macro Stress-Testing** | Caterpillar (CAT) anchor | Risk & Financial track

---

## What's in this bundle

| File | Purpose |
|---|---|
| `Risk_Audit_Capital_Deployment.ipynb` | Analytics notebook — pulls CAT financials, builds the cash flow profiles, computes σ from sector returns, generates all CSVs the Excel and Tableau pieces consume |
| `Risk_Audit_Financial_Engine.xlsx` | 9-sheet financial model — 302 formulas, all validated, zero errors. The CFO's working model. |
| `Tableau_Dashboard_Spec.md` | Step-by-step build guide for the executive dashboard (~30 min in Tableau Desktop) |

---

## Folder layout for running this

The notebook auto-resolves paths. Place files like this:

```
Module 03/
└── Track 03/
    ├── dataset/              ← drop the 5 Kaggle CSVs here
    │   ├── 2014_Financial_Data.csv
    │   ├── 2015_Financial_Data.csv
    │   ├── 2016_Financial_Data.csv
    │   ├── 2017_Financial_Data.csv
    │   └── 2018_Financial_Data.csv
    └── risk_audit/
        ├── Risk_Audit_Capital_Deployment.ipynb   ← run this
        ├── Risk_Audit_Financial_Engine.xlsx       ← already populated
        ├── Tableau_Dashboard_Spec.md              ← follow this for the dashboard
        ├── data/             (auto-created)
        ├── outputs/          (auto-created — 12 CSVs feeding Excel + Tableau)
        └── figures/          (auto-created — 3 PNGs for the appendix)
```

Dataset: [Kaggle 200 Financial Indicators of US Stocks 2014-2018](https://www.kaggle.com/datasets/cnic92/200-financial-indicators-of-us-stocks-20142018)

---

## Workflow

1. **Run the notebook** end-to-end (`Cell → Run All`). It produces 12 CSVs and 3 figures in ~15 seconds.
2. **Open the Excel engine.** Inputs are blue, formulas are black, scenario toggles are yellow. Edit blue cells to stress-test; the entire model recalculates.
3. **Build the Tableau dashboard** by following `Tableau_Dashboard_Spec.md` — every sheet, calculated field, and dashboard action is specified with the exact numbers to verify against.

---

## Headline findings

| Scenario | WACC | Domestic NPV | Outsource NPV | Winner | NPV gap |
|---|---|---|---|---|---|
| Low Growth | 6.15% | $1,259M | $855M | **Domestic** | +$404M |
| Base Case | 7.50% | $1,036M | $781M | **Domestic** | +$256M |
| High Inflation | 12.00% | $433M | $577M | **Outsource** | -$144M |

**The audit's central insight: the project ranking flips between Base Case and High Inflation.** This is exactly the macro-sensitivity finding the brief asks for.

| Project | IRR | Initial Capex | Cross-over WACC |
|---|---|---|---|
| Domestic Automation | 16.39% | $2.0B | ~10.5% — domestic wins below, outsource wins above |
| Outsourcing | 43.00% | $0.4B | (same point) |

---

## Methodology notes

**Cash flow forecast (Task 1).** Linear regression on CAT Revenue produces R² = 0.003 — meaningless because Revenue is cyclical, not trending (2016 was a clear commodity-cycle trough; Net Income went negative). Standard FP&A practice for cyclical names: use **median 5-year FCF as steady-state baseline** + explicit Low/Base/High growth scenarios (1% / 2.5% / 4%). This is what a real CFO model does.

**Risk distribution (Task 3 reframe).** The brief says "historical commodity prices"; the dataset has equity statements, not commodity time series. The reframe documented in the notebook: use the **5-year panel of annual returns across all ~500 Industrials-sector tickers (2,768 ticker-year observations)** and compute the cross-sectional σ of the sector return distribution. The statistical work — distribution analysis, σ, variance, risk-premium derivation — is identical, just on equity returns instead of commodity prices.

Pooled stats: n = 2,768, μ = 7.36%, σ = 47.18%, skewness = 2.12, excess kurtosis = 17.81 (heavily right-tailed, fat tails — characteristic of cross-sectional equity returns).

**Important calibration.** The 47% cross-sectional σ measures *spread across firms*, not single-firm volatility. Used directly as a WACC premium it would produce nonsense (50%+ discount rates). The model handles this correctly: WACC = rf + β·ERP, with ERP scaled by scenario (0.7× / 1.0× / 2.0×), giving sensible WACC values of 6.15% / 7.50% / 12.00%.

**Sensitivity grid (Task 2).** 2-way data table sweeps WACC from 5% to 15% × Price Elasticity from -2.0 to 0.0. Conditional formatting in green/yellow/red shows the cross-over diagonal. Excel formulas pull from named ranges so editing any input cascades through the whole grid.

**Dashboard actions (Task 4).** Three Tableau actions specified: a Filter action on the Scenario card (the CFO toggle the brief asks for), a Highlight action on the project line chart, and a Reset button. Verification checklist in the spec gives exact numbers to match before publishing.
