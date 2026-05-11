# 3. The Risk & Financial Track (Reframed)

**Project Title:** The "Black Swan" Audit: Stress-Testing Capital Structure under Uncertainty.

**Dataset:** [Brent Crude Oil Prices | Kaggle](https://www.kaggle.com/datasets/mabusalah/brent-oil-prices) — 9,011 daily observations (May 1987 → Nov 2022) paired with synthetic **EnergyCo** firm financials.

**Scenario:** **EnergyCo, a mid-cap energy conglomerate** ($5B total capital, equity beta 0.95 unlevered) is evaluating a **$150M offshore Brent-linked drilling project** (10-year horizon, 5,000 barrels/day production, $35/bbl extraction cost). They need to optimize their Capital Structure while protecting against "Black Swan" economic events using Quantitative Risk Assessment.

**Objective:** Run **10,000 Monte Carlo Simulations** (Schwartz mean-reverting model with Student-t innovations, ν=5.87 from GARCH-t calibration on real Brent log returns) to predict project NPV and use Black-Scholes to value the **option to abandon (Year 3) or expand (Year 5)**.

**Tasks:**

1. **Financial Theory:** Use **CAPM** (rF = 4.5%, MRP = 5.5%, β_unlevered = 0.95 from Damodaran mid-cap energy benchmark) and **Modigliani-Miller (with taxes, τ = 21%)** to determine the firm's optimal debt-to-value ratio by sweeping D/V from 0% to 80% in 5% increments with Hamada beta re-levering at each step.

2. **Simulation & Risk:** Run a **Monte Carlo Simulation in Python** (Schwartz one-factor mean-reverting OU on log prices; Student-t innovations for fat tails) to create a probability distribution of the project's NPV, reporting P5 / P50 / P95 / Probability-of-Loss / Conditional VaR.

3. **Sensitivity Analysis:** Perform a Quantitative Risk Assessment by sweeping a **2D grid of interest rate hikes (0–500 bps in 50bps steps) × Brent price shocks (−50% to +50% in 10pp steps)** to find the "Breaking Point" (viability frontier) where IRR drops below WACC.

4. **Options Pricing:** Use the Black-Scholes Model to value two **Real Options**: (a) **abandon put** (American put, K = $40M salvage, T = 3 years) and (b) **expand call** (American call, K = $60M expansion CapEx, T = 5 years), with σ_project = σ_Brent × 0.85 (dampened from commodity volatility).

**Deliverable:** A **Risk-Adjusted Financial Report** (`RiskAdjustedFinancialReport.xlsx`, 9 sheets, 676 live formulas) including (a) a **probability-based NPV Heatmap** over (Brent price × WACC) plane with breakeven contour, and (b) a **Cash Flow Forecast (Indirect Method)** with 10-year pro forma in three scenarios (P5/P50/P95) where Net Income → +D&A → ±WC change → FCF.

---

## What Changed From the Original Brief

| Item | Original | Reframed | Why |
|---|---|---|---|
| **Dataset** | All Lending Club loan data | Brent Crude Oil Prices (Kaggle: mabusalah/brent-oil-prices) | Lending Club is consumer credit risk on personal loans (FICO, charge-offs, individual debt-to-income). The brief is corporate capital structure for an energy project — completely different domain. Brent is the canonical commodity volatility for energy-project finance. |
| **Scenario specificity** | "high-risk energy project" | "$150M offshore Brent-linked drilling, 10-yr horizon, 5,000 bbl/day, $35/bbl extraction cost" | Original is too vague to drive Monte Carlo. Specificity makes revenue = production × Brent price computable per simulation path. |
| **"Black Swan" definition** | Decorative phrase | Operationalized: >3σ deviations from GARCH-fitted distribution; Student-t (ν=5.87 from MLE) residuals; calibrated against real Brent's 4.07× excess over Gaussian | Without operationalization, "Black Swan" is flavor text. Student-t residuals reproduce real Brent's fat-tail behavior (3.91× excess in simulation matches real 4.07× excess). |
| **CAPM inputs** | Generic | Specified: rF = 4.5% (10-yr Treasury), MRP = 5.5%, β_U = 0.95 (Damodaran mid-cap energy), τ = 21% | Brent prices alone don't give CAPM inputs. Citing real, sourceable assumptions keeps the analysis defensible. |
| **MM optimal D/E** | "Optimal debt-to-equity ratio" | "Optimal debt-to-value ratio" via D/V sweep with Hamada beta re-levering | D/V is the technically correct denominator for WACC computation; D/V sweep with re-levering is the standard textbook formulation. |
| **Sensitivity dimension** | "Breaking point where interest rate hikes make IRR unviable" (1D) | 2D grid: rate hikes × Brent shocks, identify viability frontier contour | 1D answer is a single number. 2D grid produces a heatmap with a contour, matching the "probability-based NPV Heatmap" deliverable language. |
| **Real options specification** | "Value 'Real Options' within the project" (vague) | Two specific options: abandon put (K=$40M, T=3) and expand call (K=$60M, T=5, V'=0.5×V0) | Without specification, "real options" is a rabbit hole. Two named options each map cleanly to Black-Scholes inputs. |
| **NPV Heatmap interpretation** | "probability-based NPV Heatmap" (ambiguous) | Density heatmap over (Brent price × WACC) plane with breakeven contour and MC P5/P50/P95 markers | Original could mean any of three visualizations. Density-with-contours is the most analytically informative. |

**What stays unchanged:** Project title, scenario hook, all four task names, both deliverable names, the decision-logic spine (optimal capital structure → simulate NPV → find breaking point → value real options).

---

## Synthetic-Anchor Disclosure

EnergyCo is a synthetic anchor: a fictional mid-cap energy conglomerate evaluating a $150M offshore drilling project. **EnergyCo's balance sheet ($5B total capital), tax rate (21%), equity beta (0.95), and project parameters (production, extraction cost, salvage value, expansion CapEx) are narrated** for boardroom credibility — same pattern as DataCo (Track 1), PivotCo (Track 2), and prior portfolio anchors. **Brent oil prices, GARCH-derived volatility, the entire NPV distribution, and all derived risk metrics (P5/P95/CVaR/PoL/option values) are real**, computed from the actual Kaggle dataset using Schwartz mean-reverting + GARCH(1,1)-Student-t. The project's revenue line is driven directly by simulated Brent price paths, so the Monte Carlo, IRR sensitivity, and Black-Scholes σ are all data-grounded.

---

## Continuity vs. Track 3 v1, v2, v3

| Aspect | v1 — RiskAudit | v2 — Automation | v3 — CapitalStructure | **v4 — Black Swan (this)** |
|---|---|---|---|---|
| Framework | CAT bonds + capital allocation | Brent-driven automation ROI | Capital structure optimization | Fat-tailed stress testing + IRR contour |
| Hero metric | $55B exposure, IRR=43% | Brent persist=0.9930, PoD 50% | Optimal D/V=30%, Real Option=$681M | **P5=−$161M, CVaR=−$221M, total options $125M** |
| Distribution assumption | Gaussian | Gaussian GARCH | Gaussian GARCH | **Student-t (ν=5.87) for fat tails** |
| Hero visual | Capital allocation pyramid | Brent vol surface | D/V optimization curve | **2D viability frontier + NPV density heatmap** |
| Sensitivity | 1D: WACC sweep | 1D: PoD vs leverage | 1D: D/V sweep | **2D: rate hike × Brent shock grid** |
| Real options | Implicit | None | Single combined ($681M) | **Two named (abandon put + expand call)** |
| Headline framing | Capital allocation | Investment hurdle | Optimal financing | **"Black Swan" stress-testing primary** |

The deliberate v4 differentiation: lead with **Black Swan stress-testing** as the headline (matches brief's exact language), use **Student-t residuals** (genuinely different from v3's Gaussian), produce a **2D viability contour** (genuinely different from v3's 1D sweep), and **explicitly specify two named real options** (genuinely different from v3's combined option figure). Same Brent dataset, deliberately orthogonal lens.
