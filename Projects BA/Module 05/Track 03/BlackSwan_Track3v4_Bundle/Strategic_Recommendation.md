# Risk-Adjusted Recommendation — Pyramid Deck Outline

**Engagement:** EnergyCo "Black Swan Audit" — Capital Structure Stress Test Track 3 v4
**Audience:** EnergyCo CFO, Treasurer, Board Risk Committee
**Format:** ~13 slides, McKinsey Pyramid Principle structure

---

## Opening Frame (SCR — Situation, Complication, Resolution question)

**Situation.** EnergyCo (mid-cap energy conglomerate, $5B total capital) is evaluating a **$150M offshore Brent-linked drilling project** (10-yr horizon, 5,000 bbl/day, $35/bbl extraction cost). The board needs to approve (or reject) the investment and choose the financing mix.

**Complication.** Brent volatility has been **40.5% annualized over 35 years** with **kurtosis of 65.9** — fat-tailed enough that a Gaussian risk model would understate >3σ events by a factor of ~4×. A naïve NPV calculation can't tell the board what they actually need to know: **how badly can this project fail under a Black Swan scenario, and how should we structure capital to survive it?**

**Question.** Given EnergyCo's risk capacity, what's the optimal capital structure for this project, and what hedges should be contractually written into the project agreement?

---

## Slide 1 — Title + Executive Summary

**Title:** *Approve at D/V = 30%, but only with the abandon option contractually written.*

**Subtitle:** *Risk-Adjusted Financial Report — 10K Monte Carlo paths, GARCH-Student-t calibration, 2D viability frontier*

**Hero box:**
> Median NPV is +$193.8M. P5 (Black Swan downside) is −$161.5M. The abandon put + expand call combine for **$125.3M of optionality value (84% of CapEx)**. With the options written into the contract, total risk-adjusted value = **$319.1M**.

**Three supporting tiles:**
- **CAPITAL STRUCTURE:** D/V = 30%, WACC = 9.35%
- **NPV DISTRIBUTION:** Median +$193.8M, P5 −$161.5M, P(loss) = 21.65%
- **REAL OPTIONS:** Abandon put + expand call = $125.3M

---

## Slide 2 — Pyramid: The Argument in One Picture

```
            TOP: Approve at D/V=30% with abandon option written into contract
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
   CAPITAL                    NPV DISTRIBUTION         REAL OPTIONS
   STRUCTURE                  Median +$194M            Abandon $0 (median)
   D/V=30%, WACC=9.35%        P5 -$162M (Black Swan)   Expand $125M (median)
   Tax shield > spread        P(loss)=22%, CVaR=-$221M Asymmetric collar
```

---

## Slide 3 — Why "Black Swan" is Real Here (Not Just Decoration)

**Headline:** *Brent's tails are 4× heavier than a Gaussian model would predict. We use Student-t to capture this.*

**Visual:** Real Brent return histogram with Gaussian overlay and Student-t (ν=5.87) overlay. Highlight: actual >3σ events vs Gaussian-expected.

| Metric | Real Brent | Gaussian baseline | Excess factor |
|---|---|---|---|
| Annualized vol | 40.53% | (any) | — |
| Kurtosis | 65.9 | 0 | n/a |
| Skewness | −1.74 | 0 | crashes worse than rallies |
| >3σ events (in 9,011 obs) | 99 | 24.3 | **4.07×** |
| >5σ events | 26 | ~0 | unbounded |

**Speaker notes:** The 2008 crash, 2014–16 supply glut, 2020 COVID demand collapse, and 2022 Russia/Ukraine shock are all in this dataset. Gaussian Monte Carlo would treat them as ~once-in-a-thousand-year events when they're actually once-in-a-decade.

---

## Slide 4 — TASK 1: CAPM + MM Optimal Capital Structure

**Headline:** *Optimal D/V = 30%. WACC bottoms at 9.35%. Tax shield wins until credit spread starts widening past 30%.*

**Visual:** WACC curve over D/V = 0–80% with optimum point highlighted; component costs (rE, rD, WACC) overlaid.

| D/V | β_levered | rE | rD | WACC |
|---|---|---|---|---|
| 0% | 0.95 | 9.73% | 5.50% | 9.73% |
| 20% | 1.14 | 10.76% | 5.50% | 9.47% |
| **30%** | **1.27** | **11.49%** | **5.50%** | **9.35% ← optimum** |
| 40% | 1.45 | 12.48% | 6.07% | 9.40% |
| 60% | 2.08 | 15.93% | 8.46% | 10.38% |
| 80% | 4.00 | 26.50% | 12.21% | 13.02% |

**Speaker notes:** Below 30% D/V, the tax shield dominates; above 30%, credit spread widening dominates. WACC curve is shallow near optimum (30–35% all give WACC within 5bps), so EnergyCo has flexibility on the exact mix.

---

## Slide 5 — TASK 2: Monte Carlo NPV Distribution

**Headline:** *Median NPV +$194M, but the distribution has a real left tail. P(loss) = 22%.*

**Visual:** NPV histogram with P5/P50/P95 vertical lines + sample of 200 Brent paths.

| Statistic | Value |
|---|---|
| Mean NPV | +$259.7M |
| P5 NPV (downside) | **−$161.5M** |
| P25 NPV | +$23.4M |
| **P50 (median)** | **+$193.8M** |
| P75 NPV | +$422.4M |
| P95 NPV (upside) | +$906.6M |
| **P(NPV < 0)** | **21.65%** |
| P(NPV < −$50M severe) | 15.25% |
| **CVaR(5%)** | **−$221.2M** (avg of worst 5%) |

**Speaker notes:** 21.65% probability of loss isn't catastrophic for a single project — but the CVaR of −$221M means *when* it goes wrong, it goes wrong by ~$60M more than the P5 alone. That's the Black Swan tail showing through.

---

## Slide 6 — Calibration Check: Simulation Reproduces Real Fat Tails

**Headline:** *3.91× excess >3σ events in simulation vs Gaussian. Real Brent: 4.07×. Calibration is honest.*

**Visual:** Side-by-side count of >3σ events in real Brent vs simulated paths vs Gaussian theory.

| Distribution | >3σ frequency | Excess factor |
|---|---|---|
| Gaussian theory | 0.27% | (baseline) |
| Real Brent (35-yr history) | 1.10% | 4.07× |
| Our simulation | 1.06% | 3.91× |

**Speaker notes:** This is the difference between a Monte Carlo that "looks scary" and one that's calibrated to reality. Our P5 of −$162M reflects real Brent's behavior, not synthetic Gaussian noise.

---

## Slide 7 — TASK 3: 2D Viability Frontier (Breaking Point)

**Headline:** *66 of 121 cells viable (54.5%). The breaking point isn't a single number — it's a contour.*

**Visual:** 11×11 heatmap (rate hike × Brent shock) with breakeven contour overlaid; color-coded by NPV.

**Key reads from the grid:**
- At base case (0bps hike, 0% shock): NPV = +$39M (viable)
- Brent −20% shock + 0bps hike: NPV = −$76M (already underwater)
- Brent −10% shock + 500bps hike: NPV = −$40M
- Brent +10% shock + 500bps hike: NPV = +$50M (still viable)
- **Brent price effect dominates.** ±10% Brent shock moves NPV by ±$55M; +500bps rate hike only moves NPV by ~$30–50M.

**Speaker notes:** Don't focus on the rate hike. Brent volatility is the real risk.

---

## Slide 8 — TASK 4: Black-Scholes Real Options

**Headline:** *Total option value = $125.3M (84% of CapEx). Asymmetric collar: abandon protects downside, expand captures upside.*

**Visual:** Option value vs V0 curve, both options overlaid, totals plotted.

| Scenario | V0 (gross PV) | Abandon Put | Expand Call | Total |
|---|---|---|---|---|
| **P5 Black Swan** | −$11.5M | **$33.95M** | $0.00M | $33.95M |
| P25 Stress | $173.4M | $0.05M | $44.82M | $44.87M |
| **P50 Median** | $343.8M | $0.00M | **$125.31M** | $125.31M |
| Mean | $409.7M | $0.00M | $174.4M | $174.4M |

**Speaker notes:** The abandon put is a deep OTM hedge that pays off only if the project tanks. The expand call is the dominant value at central case — most project optionality is upside, not downside. Together they form a collar.

---

## Slide 9 — Probability-Based NPV Heatmap (the Deliverable)

**Headline:** *NPV density over the (Brent × WACC) plane. P5 / P50 / P95 markers from Monte Carlo overlaid.*

**Visual:** 2D heatmap with breakeven contour and dotted vertical lines at MC-derived P5 ($30/bbl), P50 ($53/bbl), P95 ($122/bbl) Brent levels.

**Reading:** At WACC = 9.35% (the MM optimum), breakeven Brent is around **$50/bbl**. The MC's P5 long-run price is below breakeven — confirming the 22% loss probability geometrically.

---

## Slide 10 — Cash Flow Forecast (Indirect Method, the Other Deliverable)

**Headline:** *10-year pro forma in three scenarios. P50 base case: total FCF = $400M, NPV = +$17M (deterministic).*

**Visual:** Three stacked bar charts: P5 / P50 / P95 annual FCF.

| Year | P5 ($M) | P50 ($M) | P95 ($M) |
|---|---|---|---|
| 1 | $5 | **$43** | $135 |
| 5 | -$5 | $25 | $90 |
| 10 | -$8 | $19 | $74 |
| **10-yr total FCF** | -$30 | **$400** | $1,150 |

**Speaker notes:** P5 scenario shows the project running near break-even ops cash flow but never recovering CapEx. P50 base case is solidly positive. P95 upside is triple the base case.

---

## Slide 11 — Risk-Adjusted Approval Conditions

**Headline:** *Five conditions that turn a 22%-loss-probability project into an asymmetric collar.*

| # | Condition | Why | Trigger |
|---|---|---|---|
| 1 | D/V = 30% capital mix | WACC minimum from MM | At inception |
| 2 | Abandon option (Yr 3 put, K=$40M) | Hedges P5 Black Swan | NPV-to-go < salvage |
| 3 | Expand option (Yr 5 call, K=$60M) | Captures Brent>$90 upside | Brent > $90 sustained |
| 4 | Quarterly Brent vol monitor | GARCH persistence = 0.9930 | Vol > 50% annualized |
| 5 | Annual stress test refresh | Re-run 10K MC each cycle | Each board cycle |

**Speaker notes:** Conditions 1–3 are contractual. Conditions 4–5 are governance.

---

## Slide 12 — Honest Call-outs

- **EnergyCo is a synthetic anchor.** Per-customer Brent prices, vol, and risk metrics are real. Firm-level financials ($5B capital, beta 0.95, project params) are narrated for boardroom credibility — same pattern as our other portfolio synthetic anchors.
- **Black-Scholes uses European approximation.** American option values are bounded *above*; we're conservative.
- **σ_project = σ_Brent × 0.85** is a standard simplification. Project value depends on more than commodity price (also operations, geology), so dampened vol is appropriate.
- **Schwartz mean-reverting** is industry-standard for commodities. Alternatives (GBM, jump-diffusion) would give different tail behavior.
- **Viability contour is for $60/bbl baseline.** A different baseline shifts everything; investors should choose a baseline matching their forward curve.

---

## Slide 13 — Recommendation

**Headline:** *Approve. Conditional on contractual options. Total risk-adjusted value = $319.1M.*

**Decision:**
- ✅ **Approve** the project at D/V = 30%
- ✅ **Write the abandon put** into the project agreement (Year 3, K = $40M)
- ✅ **Write the expand call** into the project agreement (Year 5, K = $60M, threshold Brent > $90/bbl)
- 🟡 **Conditional**: quarterly Brent vol monitoring, annual stress test refresh

**Total Risk-Adjusted Value:**
- Median NPV (without options): +$193.8M
- + Abandon put value: +$0.0M (deep OTM at median)
- + Expand call value: +$125.3M
- **= TOTAL: $319.1M**

**The decision logic in one sentence:** *Without the options, this project is a 22%-loss-probability asset with median NPV $194M. With the options written in, the same project becomes a collar with downside floor at salvage and unbounded upside.*

---

## Appendix Slide A — Deliverables Inventory

- `BlackSwan_Audit.ipynb` — End-to-end notebook (4 tasks + heatmap + cash flow)
- `RiskAdjustedFinancialReport.xlsx` — 9 sheets, 676 live formulas
- `mc_simulator.py` — CLI for batch Monte Carlo (Schwartz + Student-t)
- `Project_Brief_Reframed.md` — Brief reframe with diff vs original
- `README.md` — Workflow, methodology, honest call-outs
- `data/BrentOilPrices.csv` — Source data (Kaggle blastchar)
