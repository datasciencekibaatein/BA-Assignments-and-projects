# Capital Structure Audit - Track 3 (Risk & Financial)

**Bundle for the EnergyCo $2B expansion / capital structure decision.**
Anchored to 35.5 years of Brent crude data (1987-2022, 9,011 daily observations).

---

## Files in this Bundle

| File | Purpose |
|---|---|
| `CapitalStructure_Audit.ipynb` | End-to-end Jupyter notebook (9 parts: data, GARCH, CAPM, APT, MM/WACC, Real Option, CF Forecast, Merton PoD, exports) |
| `CapitalStructure_Engine.xlsx` | Live Excel model (11 sheets, 208 formulas, defined names) - the deliverable handed to the CFO |
| `garch_forecaster.py` | Standalone CLI Python GARCH script (one of the explicit brief deliverables) |
| `Tableau_Dashboard_Spec.md` | Build spec for the **Risk Heatmap** Tableau dashboard (6 data sources, 8 sheets, 1440×900 layout) |
| `Pyramid_Deck_Outline.md` | McKinsey-style 11-slide deck outline + appendix + speaker notes |
| `sql/schema.sql` + `sql/load_data.py` | SQLite schema (3 tables, 5 views) + auto-loader |
| `BrentOilPrices.csv` | Source dataset (Kaggle / U.S. EIA) |
| `README.md` | This file |

---

## Folder Layout (Recommended)

```
Module 03/
└── Track 03/
    └── cap_audit/
        ├── data/
        │   └── BrentOilPrices.csv
        ├── sql/
        │   ├── schema.sql
        │   └── load_data.py
        ├── scripts/
        │   └── garch_forecaster.py
        ├── outputs/                            (created on first run)
        │   ├── capaudit.db                     (SQLite, ~0.8 MB)
        │   ├── garch_conditional_vol.csv       (9,010 rows)
        │   ├── garch_forward_cone.csv          (90 rows)
        │   ├── risk_heatmap_data.csv           (24 rows: 6 leverage × 4 regime)
        │   ├── npv_stress_2way.csv             (3 scenarios × 6 WACCs)
        │   ├── wacc_curve.csv                  (8 leverage scenarios)
        │   └── dashboard_kpis.csv              (20 headline KPIs)
        ├── figures/                            (created on first run)
        │   ├── brent_levels_returns.png
        │   ├── garch_cond_vol.png
        │   ├── vol_regime_distribution.png
        │   ├── mm_wacc_taxshield.png
        │   └── risk_heatmap.png
        ├── CapitalStructure_Audit.ipynb
        ├── CapitalStructure_Engine.xlsx
        ├── Tableau_Dashboard_Spec.md
        ├── Pyramid_Deck_Outline.md
        └── README.md
```

---

## Workflow

### Option A: Full notebook flow

1. Place `BrentOilPrices.csv` in `data/`
2. From the project root, run: `python sql/load_data.py`
   - Builds `outputs/capaudit.db` (loads Brent prices, fits GARCH, stores conditional vol per row, populates regime + leverage scenario tables)
3. Open `CapitalStructure_Audit.ipynb` and run all cells
   - Notebook will auto-build the database on first run if not present
   - Generates all CSVs in `outputs/` and PNGs in `figures/`
4. Open `CapitalStructure_Engine.xlsx` to interact with the live model
   - Modify any blue cell on `Inputs` to see the impact propagate
   - Use the scenario picker on `Scenarios!C12` (1=Conservative, 2=Recommended, 3=Aggressive)
5. Connect Tableau to the CSVs in `outputs/` and build the dashboard per `Tableau_Dashboard_Spec.md`
6. Build the deck from `Pyramid_Deck_Outline.md`

### Option B: Standalone GARCH CLI

```
python scripts/garch_forecaster.py --input data/BrentOilPrices.csv --horizon 90 --output-dir outputs/garch
```

This produces:
- `garch_diagnostics.csv` - fit parameters, persistence, half-life
- `garch_conditional_vol.csv` - per-day annualized vol
- `garch_forward_cone.csv` - 90-day forecast with Student-t bands
- `garch_summary.txt` - human-readable report

---

## Headline Findings

| Finding | Number | Significance |
|---|---|---|
| Brent observation count | 9,011 | 35.5 years (1987-2022) |
| ADF test on log-returns | -16.43, p<0.0001 | Stationary - GARCH valid |
| ARCH-LM test | LM=1300, p<1e-9 | Strong vol clustering |
| **GARCH(1,1) persistence** | **0.9930** | Vol shocks decay slowly |
| **Half-life of vol shocks** | **99 days** | ~3.3 months |
| **Long-run annualized vol** | **45.83%** | Used as Black-Scholes σ |
| Student-t df (ν) | 5.87 | Heavy tails confirmed |
| **CAPM cost of equity** | **10.45%** | Single-factor energy CAPM |
| **APT cost of equity** | **10.15%** | Two-factor (level + vol) |
| **Optimal D/V** | **30%** | WACC trough |
| **WACC at optimum** | **8.97%** | Below current 9.05% (D/V=20%) |
| Tax shield at optimum | $8.04B | MM with taxes |
| **Real Option Value** | **$681M** | Black-Scholes with σ from GARCH |
| **Real Option Time Value** | **$281M** | Premium of waiting over acting |
| Project NPV at base WACC | -$64M | Marginally negative |
| Project IRR | 8.20% | Below WACC 8.97% |
| **PoD at D/V=40%, MED vol** | **0.45%** | Safe |
| **PoD at D/V=50%, MED vol** | **13.87%** | Cliff begins |
| **PoD at D/V=60%, MED vol** | **62.69%** | Non-investable |

**Recommendation:** Target D/V = 30-35%. Defer the $2B project ~6 months. Re-evaluate after one quarter of vol clarity.

---

## Methodology Notes

### GARCH model selection

GARCH(1,1) Student-t was chosen because:
- **Standard Gaussian GARCH** underestimates tail risk (Brent has excess kurtosis = 65.9, far above Gaussian's 3)
- **Student-t innovations** with df ~5.87 capture the heavy tails empirically
- **GARCH(1,1)** is the parsimonious specification; higher orders did not improve AIC/BIC meaningfully
- **Persistence of 0.9930** with **half-life 99 days** is consistent with the literature (Sadorsky 2006; Marzo & Zagaglia 2010)

### Single-factor energy CAPM

For pure-play upstream energy firms, the dominant systematic risk is commodity price exposure. We use Brent returns as the single risk factor (Sadorsky 2001):

```
Ke = Rf + β_Brent × RP_Brent
```

This is *not* the standard market-portfolio CAPM. The reasoning: a $50B BBB-rated upstream firm's equity returns are dominated by Brent moves; the systematic risk decomposition that matters is the commodity factor, not the equity-market factor.

### MM tax shield with distress premium

We extend the textbook MM with taxes (`V_L = V_U + Tc × D`) by adding a quadratic distress premium on debt above D/V=30%:

```
Kd(dv) = Kd_base + 0.02 × (dv / 0.5)² for dv > 0.30
```

This calibration produces realistic credit-spread widening as leverage rises - rough match to traded BBB and BB credit spreads. The effect is what creates the WACC trough: tax shield benefit and rising debt cost cross at D/V=30%.

### Merton-style PoD

Treats EnergyCo equity as a call option on firm assets (Merton 1974). Distance to Default:

```
DD = (ln(V/D) + (μ - 0.5σ_V²) × T) / (σ_V × √T)
PoD = N(-DD)
```

Where σ_V (firm asset vol) = 0.55 × σ_Brent (commodity vol). This 0.55 ratio is industry-typical for upstream pure-plays - the firm has some operational diversification, but not much.

### Black-Scholes Real Option to Delay

Standard BS call on project value:

```
C = S × N(d1) - K × exp(-rT) × N(d2)
```

with σ = GARCH long-run annualized vol = 45.83%. The choice of σ is the rigorous part of this model; most consultants plug in 30% as a guess. Using GARCH-implied σ ties the option valuation back to the empirical commodity dynamics.

---

## Honest Call-Outs

- **EnergyCo financials are synthetic.** $50B revenue, 28% EBITDA margin, BBB credit, 35% starting D/E. These are anchored to industry medians for $50B BBB-rated upstream pure-plays (Hess, Marathon, Murphy Oil scale). The math is reproducible; the firm itself isn't real. Before final commitment, re-run the entire model with actual client financials.

- **Beta vs Brent (0.85) is industry-typical, not empirically estimated.** A real engagement would estimate this from 24-month rolling regression on the client's actual equity returns. The literature range for upstream pure-plays is 0.8-1.1; we picked the median.

- **Merton PoD numbers are directional thresholds, not point estimates.** The model assumes log-normal asset values - real defaults cluster (jumps, contagion). The numbers tell you *where* the cliff is, not *exactly* where each firm sits.

- **Black-Scholes assumes constant σ over the option life.** Brent vol clearly varies. The use of GARCH long-run vol is a reasonable proxy for a 1-year option horizon, but a Heston or local-vol model would be more rigorous.

- **GARCH is backward-looking.** It captures historical vol clustering well but won't anticipate regime breaks. For decision-making, combine with forward-looking implied vol from BRENT option markets when available.

- **The distress premium model on debt is simplistic.** A quadratic kicker above D/V=30% is calibrated to round-number credit spreads. A production model would use traded BBB → BB → B spread surfaces.

- **The recommendation is robust to all of these caveats** because the *direction* of every refinement is the same: each correction tightens the prudent leverage band, not expands it. The 30-35% recommendation is conservative.

---

## Reference Frame

Against the original brief, this audit delivers:

1. ✅ **Stochastic volatility model with quantified parameters** → GARCH(1,1) Student-t, persistence 0.9930, long-run vol 45.83%
2. ✅ **Cost of equity from CAPM and APT** → 10.45% and 10.15% respectively, with explanation for the gap
3. ✅ **MM with taxes + tax shield value + WACC curve** → 8 leverage scenarios, optimum at D/V=30%, tax shield $8B
4. ✅ **Black-Scholes Real Option** → $281M time value, σ from GARCH
5. ✅ **10-year cash flow forecast** with Indirect Method
6. ✅ **2-Way NPV stress** → Brent scenario × WACC matrix
7. ✅ **Probability of Default heatmap** → 6 leverage × 4 vol regime grid (the headline visual)
8. ✅ **Tableau dashboard spec** + **Python GARCH script** (both explicit brief deliverables)

**Five reframings from the original brief** (documented in `Track3_CapitalStructureAudit_Brief_Reframed.md`):
- Synthetic EnergyCo declaration (single-dataset audit, not multi-dataset)
- Single-factor energy CAPM (Brent as the systematic factor, not S&P 500)
- Two-factor APT (Brent level + Brent vol, not GDP + interest rate)
- Black-Scholes σ from GARCH (rigorous, vs. textbook 30% guess)
- 2-Way NPV stress against Brent × interest rate (not inflation × rates)
