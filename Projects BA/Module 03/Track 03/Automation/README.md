# Track 3 (v2) — $150M Automation Stress-Test

**GARCH-Driven Risk Audit** | IndustrialCo (generic) anchor | Brent Oil for commodity volatility | Risk & Financial track

---

## What's in this bundle

| File | Purpose |
|---|---|
| `Automation_Audit.ipynb` | Analytics notebook — Brent audit, GARCH(1,1) fit + diagnostics, 10,000-path Monte Carlo, NPV distribution, 2-way PoD grid with bootstrap CIs, 6 CSV outputs + 6 PNG figures |
| `Automation_Audit_Engine.xlsx` | 8-sheet financial model — 152 formulas, all validated zero errors. 10-year cash flow (Indirect Method), NPV/IRR engine, Macro-Shock Scenario Manager (5 scenarios), 2-way deterministic sensitivity grid, GARCH-derived PoD constants |
| `Tableau_Dashboard_Spec.md` | Step-by-step build guide for the Risk Heatmap, 7 sheets + 3 dashboard actions |

---

## Folder layout for running this

```
Module 03/
└── Track 03_v2/
    └── automation_audit/
        ├── data/
        │   └── BrentOilPrices.csv               ← place Brent CSV here
        ├── outputs/                              (auto-created — 6 CSVs + 2 NumPy arrays)
        ├── figures/                              (auto-created — 6 PNGs)
        ├── Automation_Audit.ipynb               ← run this first
        ├── Automation_Audit_Engine.xlsx
        ├── Tableau_Dashboard_Spec.md
        └── README.md
```

Dataset: [Brent Oil Prices on Kaggle](https://www.kaggle.com/datasets/mabusalah/brent-oil-prices) — 9,011 daily prices, 1987-2022.

---

## Workflow

1. **Run the notebook** end-to-end (`Cell → Run All`). It produces 6 CSVs + 6 figures in ~60 seconds (Monte Carlo simulation is the slow step).
2. **Open the Excel engine.** Inputs are blue, formulas are black, scenario toggles are yellow. Edit the **Active Scenario** picker on the `Macro_Shocks` sheet (cell C12) to flip between Baseline / Rate Shock / Demand Shock / Combined Stress / Brief Stress.
3. **Build the Tableau Risk Heatmap** by following `Tableau_Dashboard_Spec.md`. The PoD heatmap is the hero chart.

---

## Headline findings

### The Audit's Hero Finding: Deterministic Says Accept; Monte Carlo Says Coin Flip

| Metric | Base case | Rate Shock (+2pp) | Demand Shock (-15%) | Combined Stress |
|---|---:|---:|---:|---:|
| **WACC** | 10% | 12% | 10% | 12% |
| **Demand shift** | 0% | 0% | -15% | -15% |
| **NPV (deterministic)** | **+$14.9M** | +$1.1M | -$6.4M | **-$18.4M** |
| **IRR (deterministic)** | 12.18% | — | — | — |
| **Decision (deterministic)** | ACCEPT | ACCEPT | REJECT | REJECT |
| **P(NPV<0) — Monte Carlo** | **50.1%** | 54.3% | 57.2% | **63.6%** |
| **95% CI (PoD)** | [49.0%, 51.1%] | [53.4%, 55.4%] | [56.2%, 58.1%] | [62.6%, 64.6%] |

**Read the table top-to-bottom:** the deterministic and probabilistic views disagree. Deterministic NPV at base case is mildly positive (+$15M). But once GARCH-driven oil-price volatility is layered in via 10,000 Monte Carlo paths, **half of those paths produce NPV<0 even with no rate or demand shock**. The brief's stress case is barely negative deterministically (-$18M) but has a 64% Probability of Default once oil volatility is modelled.

The hidden risk is **commodity input cost volatility**, not interest rates or demand.

### GARCH(1,1) Calibration

Fitted to 9,010 daily Brent log-returns (1987-2022), Student-t errors:

| Parameter | Value | Interpretation |
|---|---:|---|
| α (ARCH) | 0.0831 | New-shock loading |
| β (GARCH) | 0.9100 | Persistence loading |
| **Persistence (α+β)** | **0.9930** | Near-unit-root — vol shocks decay extremely slowly |
| **Half-life of shock** | **99 days** | A vol spike takes ~3 months to halve |
| Long-run annualised vol | 45.83% | Higher than equity, lower than crypto |
| Student-t df (ν) | 5.87 | Very fat tails (normal would be ν → ∞) |

**Brent's volatility is exactly what GARCH was designed for.** ARCH-LM statistic = 1,542 (p ≈ 0); ACF of squared standardised residuals is flat after fit; QQ plot tracks Student-t cleanly. The model is well-specified.

### 2-Way PoD Grid (full sweep)

| Demand \ WACC | 8% | 9% | 10% | 11% | 12% | 13% | 14% |
|---|---:|---:|---:|---:|---:|---:|---:|
| **0%** | 46.8% | 48.3% | **50.1%** | 52.2% | 54.3% | 56.6% | 59.3% |
| -5% | 48.1% | 50.0% | 52.2% | 54.4% | 56.8% | 59.5% | 62.5% |
| -10% | 50.0% | 52.2% | 54.4% | 57.0% | 59.7% | 63.0% | 66.6% |
| **-15%** | 52.2% | 54.4% | 57.1% | 59.9% | **63.6%** | 67.1% | 70.8% |
| -20% | 54.7% | 57.5% | 60.4% | 64.1% | 67.8% | 71.6% | **75.7%** |

PoD ranges from 47% (best — low rates, no demand shock) to 76% (worst — high rates and severe demand drop). **Even the best cell is a near-coin-flip.** The asymmetry comes from Brent's left-skew (-1.74) and excess kurtosis (66) — fat-tail downside scenarios dominate the upside even when central tendency is benign.

---

## Methodology notes

### Why this audit is different from a textbook NPV/IRR exercise

Standard sensitivity analysis sweeps WACC and demand assumptions in a 2-way grid (the brief's Task 3). It captures **deterministic** sensitivity to two specific drivers but misses:

- **Non-linearity** — energy shocks compound year-over-year
- **Fat tails** — the worst paths are far worse than a 2σ shift would imply
- **Volatility clustering** — a vol spike in Y1 is more likely to be followed by another vol spike in Y2 than calm conditions

GARCH captures all three. We then layer it onto the 2-way grid as a **probabilistic overlay** — for each (WACC, Demand) cell, we run 10,000 Monte Carlo paths driven by GARCH-simulated oil shocks and compute Probability of Default with bootstrap confidence intervals.

### Forward simulation assumptions

- **Drift (μ_forward) = 0** for log-returns. Historical μ in the GARCH fit (0.057%/day) reflects the 1987-2022 price-level rise from $18 to $93 — that's inflation/real-economy noise we don't project forward as a guaranteed drift. Standard practice in commodity Monte Carlo is to simulate **price ratios** around a deterministic baseline; price level is handled in the financial model separately.
- **Oil multipliers capped at [0.10x, 5.00x]** for economic plausibility. Without capping, log-normal tails from heavy-tailed Student-t residuals produce physics-violating prices (sub-$2/bbl or super-$500/bbl) over 10 years. The cap affects ~6% of paths at the floor and ~16% at the ceiling.
- **Bootstrap CIs:** 1,000 resamples per cell, 95% percentile method. CI widths are ±1pp on PoD, reflecting the precision of 10K-path Monte Carlo.

### Project assumptions (all editable in `Inputs` sheet)

| Parameter | Value |
|---|---:|
| Revenue Y0 | $1B |
| Gross margin | 60% |
| Energy / COGS | 8% (Y0 energy = $32M) |
| Tax rate | 25% |
| Capex | $150M |
| Year 1 labor savings | $28M |
| Labor savings growth | 2.5%/yr |
| Revenue growth | 3%/yr |
| Depreciation | $15M/yr (10-yr straight-line) |
| Project horizon | 10 years |

### Recommendations for the CFO

1. **Hedge 50%+ of Year 1-3 energy exposure** before any capital deployment. Oil futures or a long-term supply contract dramatically reduces the PoD by capping the left tail of the NPV distribution.
2. **Phase the capex 50/50.** Deploy $75M now, second tranche after Year 3 contingent on commodity-regime check. Optionality is worth more than a marginal IRR improvement at this risk profile.
3. **Re-run the audit annually.** GARCH persistence of 0.993 means today's volatility regime conditions next year's risk — the parameters need re-fitting as new data arrives.
4. **Don't over-index on the 2-way table.** The brief's deterministic stress (-$18M) understates the actual risk. The honest framing is "50-64% Probability of Default depending on macro" — that's the conversation the CFO should be having with the board.
