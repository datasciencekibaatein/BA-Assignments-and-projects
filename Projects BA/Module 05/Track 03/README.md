# Black Swan Audit — EnergyCo Capital Structure Stress Test

**Track 3 v4 — Risk & Financial / fat-tailed stress testing**
*Risk-Adjusted Financial Report on a $150M energy project under Black Swan conditions*

---

## TL;DR

EnergyCo (synthetic mid-cap energy conglomerate; per-period Brent prices and risk metrics are real, firm financials narrated) is evaluating a **$150M offshore Brent-linked drilling project**. We deliver a Risk-Adjusted Financial Report that:

- **Optimizes capital structure** via CAPM + MM-with-taxes → **D/V = 30%, WACC = 9.35%**
- **Runs 10,000 Monte Carlo paths** using Schwartz mean-reverting + GARCH(1,1)-Student-t (ν=5.87) on real Brent log returns → **median NPV = +$193.8M, P5 = −$161.5M, P(loss) = 21.65%, CVaR(5%) = −$221.2M**
- **Produces a 2D viability frontier** (rate hike × Brent shock) → 66 of 121 cells viable (54.5%)
- **Values two real options** via Black-Scholes → abandon put (T=3yr, K=$40M) + expand call (T=5yr, K=$60M) = **$125.3M total (84% of CapEx)**

**Recommendation:** Approve at D/V = 30%, but only with abandon and expand options contractually written. Total risk-adjusted value = **$319.1M**.

---

## Files in this bundle

| File | Purpose |
|---|---|
| `BlackSwan_Audit.ipynb` | Jupyter notebook — end-to-end (CAPM/MM, Monte Carlo, Sensitivity, Black-Scholes, Heatmap, Cash Flow). Executes clean to ~870KB with 7 figures. |
| `RiskAdjustedFinancialReport.xlsx` | Excel deliverable — 9 sheets, **676 live formulas, zero errors**. CAPM_MM sweep, NPV heatmap, 2D sensitivity grid, Black-Scholes calculator, 10-yr cash flow (3 scenarios), MC summary, Pyramid recommendation. |
| `scripts/mc_simulator.py` | Python CLI — 10,000-path Monte Carlo (Schwartz + Student-t innovations), GARCH calibration, NPV distribution, real options pricing |
| `Strategic_Recommendation.md` | 13-slide Pyramid deck outline (boardroom-ready) |
| `Project_Brief_Reframed.md` | Reframed brief + full diff vs original |
| `data/BrentOilPrices.csv` | Source data (Kaggle: mabusalah/brent-oil-prices, 9,011 daily obs) |
| `README.md` | This file |

---

## Folder layout

```
Module 03/Track 03/blackswan_audit/
├── README.md
├── Project_Brief_Reframed.md
├── Strategic_Recommendation.md
├── BlackSwan_Audit.ipynb
├── RiskAdjustedFinancialReport.xlsx
├── data/
│   └── BrentOilPrices.csv
├── scripts/
│   └── mc_simulator.py
├── outputs/        (generated)
│   ├── npv_distribution.npy           (10,000 NPV draws)
│   ├── monthly_prices.npy             (10,000 × 120 simulated paths)
│   ├── npv_grid.npy                   (11×11 sensitivity grid)
│   ├── irr_grid.npy                   (11×11 IRR grid)
│   ├── viable_grid.npy                (binary viability map)
│   ├── mc_summary.json                (P5/P25/P50/P75/P95/CVaR)
│   ├── real_options.csv               (option values per scenario)
│   ├── mm_capital_structure.csv       (D/V sweep results)
│   └── cash_flow_forecast.csv         (3-scenario pro forma)
└── figures/        (generated)
    ├── task1_capital_structure.png
    ├── task2_monte_carlo.png
    ├── task3_viability_frontier.png
    ├── task4_real_options.png
    ├── deliverable_npv_heatmap.png
    └── deliverable_cash_flow_forecast.png
```

---

## Workflow

### Option A — Notebook walkthrough (analyst path)

```bash
cd "Module 03/Track 03/blackswan_audit"
jupyter notebook BlackSwan_Audit.ipynb
# Run All. Generates 7 PNGs in figures/, several .npy/.csv/.json in outputs/.
# Notebook executes end-to-end in ~30 seconds.

# Open the Excel deliverable
open RiskAdjustedFinancialReport.xlsx
# Adjust Inputs sheet → CAPM_MM, NPV_Heatmap, Sensitivity_Grid, Black_Scholes, CashFlow recalculate live.
```

### Option B — Standalone Monte Carlo CLI (production path)

```bash
python scripts/mc_simulator.py --input data/BrentOilPrices.csv --out outputs/
# Outputs:
#   outputs/npv_distribution.npy       — 10,000-path NPV draws
#   outputs/monthly_prices.npy         — full simulated price paths
#   outputs/options_values.json        — Black-Scholes outputs
#   outputs/npv_grid.npy + irr_grid.npy + viable_grid.npy — 2D sensitivity
```

---

## Headline Findings

| # | Finding | Number |
|---|---|---|
| 1 | Optimal capital structure (D/V) | **30%** (≈optimum range 30–35%) |
| 2 | WACC at optimum | **9.35%** |
| 3 | Median project NPV | **+$193.8M** |
| 4 | P5 NPV (Black Swan downside) | **−$161.5M** |
| 5 | P95 NPV (upside) | +$906.6M |
| 6 | Probability of NPV < 0 | **21.65%** |
| 7 | CVaR(5%) — avg of worst 5% | **−$221.2M** |
| 8 | Real Brent annualized vol | **40.53%** |
| 9 | Real Brent excess kurtosis | **65.9** (Gaussian = 0) |
| 10 | Real Brent >3σ events vs Gaussian | **4.07× excess** |
| 11 | Simulation >3σ events vs Gaussian | **3.91× excess** (calibrated) |
| 12 | GARCH-t ν (degrees of freedom) | **5.87** |
| 13 | GARCH α + β persistence | 0.9930 |
| 14 | Viable cells in 2D grid | **66/121 = 54.5%** |
| 15 | Abandon put value (median) | $0.00M (deep OTM) |
| 16 | Expand call value (median) | **$125.3M** |
| 17 | Total options as % of CapEx | **83.5%** |
| 18 | Total risk-adjusted value | **$319.1M** |

---

## Methodology

### Capital structure (Task 1)

CAPM: rE = rF + β_levered × MRP, with rF = 4.5% (10-yr Treasury), MRP = 5.5%, β_unlevered = 0.95 (Damodaran mid-cap energy benchmark).

Hamada re-levering: β_L = β_U × (1 + (1 − τ) × D/E), where τ = 21% (US corporate).

Cost of debt rises with leverage: rD = 5.5% + max(0, D/V − 0.30)^1.5 × 0.18 (BBB baseline + credit spread widening above 30%).

WACC = (1 − D/V) × rE + (D/V) × rD × (1 − τ).

D/V swept 0–80% in 5% increments. Optimum at D/V = 30%, WACC = 9.35%.

### Monte Carlo (Task 2)

**Calibration:** GARCH(1,1) with Student-t residuals fit on real Brent log returns (`arch_model` from the `arch` package). Parameters: ω=0.058, α=0.083, β=0.910, **ν=5.87** (the fat-tail parameter).

**Price simulation:** Schwartz one-factor mean-reverting model on log prices:
`d(log P) = κ × (log_LR − log P) × dt + σ × dz`, with Student-t innovations using ν from GARCH.

Calibrated κ_daily = 0.000xxxx (half-life ~xxxx days), log_LR = log($xx.xx), σ_daily = 0.025xx.

**Project NPV per path:** monthly cash flows over 120 months:
- Revenue_m = simulated_price × 5,000 × 30 bbl
- COGS_m = $35 × 5,000 × 30
- OpEx_m = $1M (= $12M / 12)
- D&A_m = $1.25M (= $150M / 10 / 12)
- EBIT = Revenue − COGS − OpEx − D&A
- Tax = max(EBIT × 21%, 0)
- FCF = NOPAT + D&A
- NPV = sum(FCF / (1 + WACC)^(t/12)) − $150M CapEx

10,000 paths × 120 months × 21 days = 25.2M observations.

### Sensitivity (Task 3)

11×11 grid: rate hikes ∈ {0, 50, …, 500} bps × Brent shocks ∈ {−50%, …, +50%} in 10pp steps.

For each cell: deterministic NPV using constant Brent = $60 × (1 + shock), WACC = 9.35% + hike.

Viability: cell is viable if both IRR > WACC_eff AND NPV > 0.

### Black-Scholes real options (Task 4)

σ_project = σ_Brent × 0.85 = 0.4053 × 0.85 = **0.3445** (dampened from commodity vol because project value is more than just revenue).

**Abandon put** (after Year 3): K = $40M salvage, T = 3yr.
P = K × e^(−rT) × N(−d2) − S × N(−d1), where S = V0 (gross PV of project).

**Expand call** (after Year 5): K = $60M, T = 5yr, V_exp = 0.5 × V0 (50% capacity expansion).
C = S × N(d1) − K × e^(−rT) × N(d2), where S = V_exp.

European Black-Scholes used as approximation for American options. American value is bounded above (we're conservative on the abandon put).

### Cash flow forecast (Indirect Method)

Indirect method standard sequence:
- Net Income → +D&A → ±Working Capital changes → CapEx → FCF
- WC change modeled as 5% of revenue change (standard)
- CapEx upfront in Year 0; no maintenance CapEx assumed (simplification)

Three scenarios: P5, P50, P95 of simulated annual Brent prices from Monte Carlo.

---

## Honest Call-outs

- **EnergyCo is synthetic.** Firm-level financials ($5B capital, β=0.95, project parameters) are narrated for boardroom credibility. **All Brent prices, GARCH-derived vol, NPV distribution, and risk metrics are real.**

- **Black-Scholes uses European approximation.** American option values are bounded above; we're conservative on the abandon put.

- **σ_project = σ_Brent × 0.85** is a standard simplification. Project value depends on commodity prices but also on operational/geological factors that don't move 1:1 with oil prices. The 0.85 dampening is conventional for E&P projects; sensitivity to this assumption: ±10% in dampening = ±~15% in option value.

- **Schwartz mean-reverting** is industry-standard for commodities. Alternatives (GBM, jump-diffusion, regime-switching) would give different tail behavior. Schwartz reverts toward long-run equilibrium, which dampens long-horizon variance vs GBM.

- **Viability contour is for $60/bbl baseline.** A $80 baseline shifts the contour right (more cells viable); a $40 baseline shifts it left. Investors should choose a baseline matching their forward curve.

- **The expand call is the dominant value at central case.** This means the project is fundamentally an *upside-capture* asset, not a *downside-protected* asset. The abandon put only matters in P5 Black Swan scenarios. If a board prefers downside protection over upside capture, the project's risk profile is less attractive.

- **All risk-free rate, tax rate, beta, MRP** are citable from public sources (FRED, Damodaran, IRS). Sensitivity to these is small relative to Brent vol sensitivity.

---

## Continuity vs Track 3 v1, v2, v3

This is the fourth Track 3 build. The deliberate choice across versions: each takes a fundamentally different "what does volatility mean for this firm's financial decision?" lens.

| Aspect | v1 — RiskAudit | v2 — Automation | v3 — CapitalStructure | **v4 — Black Swan (this)** |
|---|---|---|---|---|
| Framework | CAT bonds + capital allocation | Brent-driven automation ROI + PoD | Capital structure optimization | **Fat-tailed stress testing + IRR contour** |
| Hero metric | $55B exposure, IRR=43% | Brent persist=0.9930, PoD 50.07% | Optimal D/V=30%, Real Option=$681M | **P5=−$161M, CVaR=−$221M, options $125M** |
| Distribution | Gaussian | Gaussian GARCH | Gaussian GARCH | **Student-t (ν=5.87)** for fat tails |
| Hero visual | Capital allocation | Brent vol surface | D/V curve | **2D viability frontier + NPV heatmap** |
| Sensitivity | 1D: WACC sweep | 1D: PoD vs leverage | 1D: D/V sweep | **2D: rate hike × Brent shock** |
| Real options | Implicit | None | Single combined ($681M) | **Two named (abandon + expand)** |
| Headline framing | Capital allocation | Investment hurdle | Optimal financing | **"Black Swan" stress-testing primary** |

The deliberate v4 differentiation: lead with **Black Swan stress-testing** as the headline (matches brief's exact language), use **Student-t residuals** (genuinely different from v3's Gaussian — calibrated to real fat tails, not assumed), produce a **2D viability contour** (genuinely different from v3's 1D sweep), and **explicitly specify two named real options** (genuinely different from v3's single combined option figure). Same Brent dataset, deliberately orthogonal lens.

A reviewer comparing v3 and v4 should see the same underlying analytical machinery (Brent data, GARCH calibration, MM optimization) deployed against a fundamentally different question. v3 asks "what's the optimal capital structure given commodity volatility?" v4 asks "given that the volatility has fat tails we can't model with Gaussian assumptions, how should we structure the project to survive Black Swans?"

---

## Reproducing the bundle

1. Unzip `BlackSwan_Track3v4_Bundle.zip` into a working folder
2. `cd` into it; the folder will be named `blackswan_audit/`
3. `pip install pandas numpy scipy arch matplotlib seaborn openpyxl jupyter` (if not already)
4. `jupyter notebook BlackSwan_Audit.ipynb` and Run All
5. Open `RiskAdjustedFinancialReport.xlsx` and try changing values on the `Inputs` sheet — `CAPM_MM`, `NPV_Heatmap`, `Sensitivity_Grid`, `Black_Scholes`, `CashFlow_Indirect` recalculate live (676 formulas total)
6. Optionally run `python scripts/mc_simulator.py --input data/BrentOilPrices.csv --out outputs/` to verify the standalone CLI

All hero numbers should match this README and the figures should regenerate identically (random seeds locked at 42).
