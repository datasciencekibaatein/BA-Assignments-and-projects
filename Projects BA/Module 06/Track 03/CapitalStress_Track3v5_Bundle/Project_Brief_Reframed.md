# Reframed Brief — Track 3 v5

## Project Title
**Capital Structure Optimization: Resilience Modeling in Volatile Markets**

## Scenario
A US manufacturing conglomerate ("MetalForge Industries", synthetic name) plans a $200M debt-funded expansion. Revenue baseline $1.5B, project life 10 years, target capacity addition ~$300M annual incremental revenue at maturity. Competition is intensifying; raw material costs (Brent oil derivatives) are volatile; rate environment is rising (DGS10 4.23%, BAA 6.03%); inflation tail risks (CPI 3.3%, PPI 6.0%) are material.

The Board needs a **stress-tested, risk-adjusted valuation audit** — not a glossy DCF. They want to know:
1. What is the *optimal* capital structure (not the peer-default)?
2. What is the *probability* the project underperforms its cost of capital?
3. What is the *flexibility value* of the option to expand at year 5?
4. Where does the project *break* under operational stress?

## Objective
Produce a coherent risk-adjusted valuation framework that integrates:
- **Static optimization** (where to set leverage and discount rate)
- **Probabilistic risk** (P(IRR < WACC) under stochastic shocks)
- **Strategic flexibility** (real option to expand)
- **Operational sensitivity** (breaking-point under DuPont stress)

## Tasks
1. Calibrate **MetalForge** financials against the median of 455 Industrials peer firms (real 2018 filings, cleaned for revenue > $100M and positive equity).
2. Pull live FRED parameters: DGS10 (Rf), BAA + AAA (cost of debt), CPI + PPI (inflation factors).
3. Compute **cost of equity** via both CAPM (single-factor) and APT (3-factor: market + inflation + credit). Blend the two for a multi-factor anchored Ke.
4. Run **Modigliani-Miller with taxes** to find the WACC-minimizing D/V, allowing for non-linear distress costs past 40% leverage.
5. Build a **10-year project cash flow** (Indirect Method) using peer-calibrated EBITDA margin, NWC, capex, terminal growth.
6. Fit **GARCH(1,1)** on 35 years of daily Brent log returns. Use long-run vol for both Monte Carlo and Black-Scholes.
7. Run **10,000 Monte Carlo simulations** with stochastic revenue growth, EBITDA margin, and oil-driven COGS shocks. Compute P(IRR < WACC) and P(NPV < 0).
8. Value the **option to expand at Year 5** ($100M strike for 50% capacity addition) via **Black-Scholes**.
9. Build a **2-way DuPont data table** showing DSCR (debt-service coverage) under (Asset Turnover, Net Margin) joint stress. Identify covenant breaking points.
10. Synthesize into a **Pyramid Principle deck** (SCR opening, MECE analysis, recommendation, risks).

## Deliverable
- **Risk-Adjusted Valuation Audit** (Jupyter notebook, 28 cells, 7 figures)
- **Excel Financial Engine** (11 sheets, 381 formulas, 37 defined names — fully formula-driven)
- **CLI runner** (Python script, end-to-end reproducible)
- **Strategic Recommendation deck** (13-slide Pyramid outline)
- **Reframed brief + README**

---

## Diff vs Original Brief

| Aspect | Original brief | This v5 build |
|---|---|---|
| Datasets | LendingClub + FRED | **FRED + 455 Industrials peers + Brent** |
| Reason for change | LendingClub is consumer-loan data, irrelevant for manufacturing capital structure | Industrials peer filings give real benchmarks for D/V, EM, AT, tax rate; Brent is the realistic raw-material vol driver for manufacturing |
| Scope match | Capital structure for manufacturing | ✅ better-fit data |
| Methods | "MM, GARCH, MC" | ✅ all present, plus APT, Black-Scholes, DuPont 2-way DT |

The pivot **better serves the brief's spirit** (manufacturing capital structure under volatility) than literal LendingClub usage would have.

---

## Continuity vs Prior Tracks

| | Track 3 v1 RiskAudit | v2 Automation | v3 CapStruct | v4 BlackSwan | **v5 (this)** |
|---|---|---|---|---|---|
| Hero data | CAT bonds | Brent | EnergyCo synth | EnergyCo synth | **FRED + 455 real peers + Brent** |
| Cost of equity | n/a | n/a | CAPM | CAPM | **CAPM + 3-factor APT** ⭐ |
| Distress model | n/a | n/a | static | Black Swan tail | **2-way DuPont DT** ⭐ |
| Calibration | synth | synth | synth | synth | **real peer medians** ⭐ |
| Real option | implicit | n/a | static | implicit | **explicit Black-Scholes** ⭐ |
| Final deliverable | dashboard | dashboard | model | tail-risk report | **risk-adjusted valuation audit** |

v5 is the *culmination* of the Track 3 family: real peer data + multi-factor cost of equity + explicit real option + 2-way operational stress.
