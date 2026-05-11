# Tableau Dashboard Specification - "Risk Heatmap"

**Track 3 - Capital Structure Audit | EnergyCo + Brent Crude (1987-2022)**

This spec defines a Tableau dashboard for the EnergyCo capital-structure audit. The headline visual is the **Risk Heatmap** (leverage × Brent vol regime → probability of default), surrounded by KPIs, the GARCH conditional-vol time series, the WACC curve, and the NPV stress matrix.

> **Tooling note.** This brief explicitly specifies Tableau (not Power BI). The data sources are the CSVs produced by the notebook in `outputs/`. All calculated fields use Tableau syntax.

---

## Data Sources

Connect 5 CSV files from the project's `outputs/` directory:

| Source | File | Rows | Purpose |
|---|---|---|---|
| `dashboard_kpis` | `dashboard_kpis.csv` | 20 | Headline KPI strip |
| `garch_conditional_vol` | `garch_conditional_vol.csv` | 9,010 | Brent price + cond vol time series |
| `garch_forward_cone` | `garch_forward_cone.csv` | 90 | 90-day forward vol forecast |
| `wacc_curve` | `wacc_curve.csv` | 8 | WACC curve across leverage scenarios |
| `risk_heatmap_data` | `risk_heatmap_data.csv` | 24 | PoD by leverage × vol regime |
| `npv_stress_2way` | `npv_stress_2way.csv` | 3 | NPV stress matrix |

All sources should use Tableau Live connection (CSV refresh on open).

---

## Calculated Fields

### `garch_conditional_vol` source

```
[Vol_Regime]
IF [cond_vol_annualized_pct] < 28 THEN "LOW"
ELSEIF [cond_vol_annualized_pct] < 37 THEN "MEDIUM"
ELSEIF [cond_vol_annualized_pct] < 60 THEN "HIGH"
ELSE "CRISIS"
END

[Date_Parsed]
DATEPARSE("yyyy-MM-dd", [date])

[Year]
YEAR([Date_Parsed])
```

### `risk_heatmap_data` source

```
[PoD_Pct]
[probability_of_default] * 100

[PoD_Bucket]
IF [probability_of_default] < 0.01 THEN "Safe (<1%)"
ELSEIF [probability_of_default] < 0.15 THEN "Caution (1-15%)"
ELSE "Cliff (>15%)"
END

[DV_Label]
STR(INT([dv_ratio] * 100)) + "%"
```

### `wacc_curve` source

```
[WACC_Pct]
[wacc_pct] * 100

[Optimal_Marker]
IF [wacc_pct] = WINDOW_MIN([wacc_pct]) THEN "Optimal" ELSE "" END

[DV_Label]
STR(INT([dv_ratio] * 100)) + "%"
```

### `npv_stress_2way` source

Pivot the WACC columns into long format using Tableau's pivot feature:
- Pivot fields: `wacc_7`, `wacc_8`, `wacc_9`, `wacc_10`, `wacc_11`, `wacc_12`
- Pivot field name: `WACC_Label`
- Pivot field value: `NPV_M`

Then create:

```
[WACC_Pct_Numeric]
INT(REPLACE([WACC_Label], "wacc_", ""))

[NPV_Bucket]
IF [NPV_M] > 100 THEN "Strong positive (>$100M)"
ELSEIF [NPV_M] > 0 THEN "Marginal positive (0-$100M)"
ELSEIF [NPV_M] > -300 THEN "Marginal negative (-$300M to 0)"
ELSE "Destructive (<-$300M)"
END
```

---

## Sheets / Visuals (8 total)

### 1. KPI Strip (header)

A row of 6 KPI cards showing the audit's hero numbers.

| KPI | Source | Format | Color |
|---|---|---|---|
| GARCH Persistence | `dashboard_kpis` | 0.9930 | Navy |
| Half-Life (days) | `dashboard_kpis` | 99.2 | Navy |
| Long-Run Vol | `dashboard_kpis` | 45.83% | Navy |
| Optimal D/V | `dashboard_kpis` | 30% | Green |
| Optimal WACC | `dashboard_kpis` | 8.97% | Green |
| Real Option Value | `dashboard_kpis` | $681M | Orange |

Build: 6 separate text-only sheets, each with a single KPI value as the only mark. Font sizes: label 12pt, value 28pt bold. Dashboard arrangement: horizontal row at the top.

### 2. Brent Spot + Conditional Vol Time Series (overlay)

Dual-axis line chart spanning 1987-2022.

- **Source**: `garch_conditional_vol`
- **Primary axis (left)**: Brent price ($/bbl), navy line, 0.7 thickness
- **Secondary axis (right)**: GARCH conditional vol annualized %, red line, 0.7 thickness
- **X axis**: continuous date
- **Tooltip**: Date, Price, Cond Vol %, Vol Regime
- **Annotations**: text marks at 1990 (Gulf War), 2008 (GFC), 2014 (oil glut), 2020 (COVID)
- **Title**: "Brent Crude Price vs GARCH Conditional Volatility (1987-2022)"

### 3. Vol Regime Distribution (histogram)

Stacked column chart showing percent of history in each vol regime.

- **Source**: `garch_conditional_vol`
- **Marks**: bar
- **Columns**: `[Vol_Regime]` (sorted LOW → CRISIS)
- **Rows**: COUNT(rows) / TOTAL(COUNT(rows)) → as Percentage of Total
- **Color**: by `[Vol_Regime]`: LOW=#2E7D32 (green), MED=#1F3864 (navy), HIGH=#E07A1F (orange), CRISIS=#C00000 (red)
- **Label**: percentage on each bar
- **Title**: "Time in Each Vol Regime (1987-2022)"

### 4. GARCH 90-Day Forward Vol Cone

Line chart showing the projected forward vol.

- **Source**: `garch_forward_cone`
- **Columns**: `days_ahead` (continuous)
- **Rows**: `fwd_vol_annualized_pct`
- **Reference line**: long-run vol = 45.83% (dashed red, label "Long-run vol")
- **Marks**: line, navy, 2px
- **Title**: "GARCH 90-Day Forward Volatility Forecast"

### 5. WACC Curve with Optimal Marker

Line chart with point highlight for optimum.

- **Source**: `wacc_curve`
- **Columns**: `dv_ratio` (continuous, formatted as %)
- **Rows**: `wacc_pct` (continuous, formatted as %)
- **Marks**: line + circle markers
- **Highlight**: circle at optimum filled green, label "Optimal: 30% / 8.97%"
- **Reference band**: shade D/V 30%-40% lightly (#E8F5E8) labeled "Recommended Band"
- **Title**: "WACC Curve - The Optimal Capital Structure Trough"

### 6. MM Tax Shield Bar Chart

Vertical bar chart showing $ value of tax shield by leverage.

- **Source**: `wacc_curve`
- **Columns**: `[DV_Label]` (discrete)
- **Rows**: `tax_shield` (continuous, in $B)
- **Color**: green gradient (light green to dark green) by `tax_shield` value
- **Label**: tax shield $ on each bar
- **Title**: "MM Tax Shield Value ($B) by Leverage Level"

### 7. RISK HEATMAP (THE HEADLINE)

The marquee visual. Heatmap of leverage × vol regime → PoD.

- **Source**: `risk_heatmap_data`
- **Columns**: `vol_regime` (LOW, MEDIUM, HIGH, CRISIS in that order)
- **Rows**: `[DV_Label]` sorted ascending (20%, 30%, 40%, 50%, 60%, 70%)
- **Marks**: square (large)
- **Color**: continuous on `[probability_of_default]`, gradient navy → green → amber → red, stepped at 1%, 15%, 50%
- **Label**: PoD percentage on each cell (e.g., "0.45%", "62.69%")
- **Tooltip**: D/V, Vol Regime, Brent vol assumed, Asset vol implied, Distance to Default, PoD
- **Title**: "Risk Heatmap: 1-Year Probability of Default | Leverage × Brent Vol Regime"
- **Annotation overlay**: arrow + text "Cliff between 50% and 60%" pointing to the 50→60 row transition

### 8. NPV 2-Way Stress Matrix

Heatmap-style cross-tab.

- **Source**: `npv_stress_2way` (after pivot)
- **Columns**: `[WACC_Pct_Numeric]` (continuous, sorted ascending)
- **Rows**: `scenario` (Bear, Base, Bull)
- **Marks**: square
- **Color**: continuous on `[NPV_M]`, gradient red (negative) → white (zero) → green (positive)
- **Label**: `[NPV_M]` formatted as $###M with sign
- **Title**: "Project NPV ($M): Brent Scenario × WACC"

---

## Dashboard Layout (1440 × 900)

```
┌─────────────────────────────────────────────────────────────────────┐
│ TITLE BAR: "Capital Structure Audit | EnergyCo + Brent (1987-2022)" │
├─────────────────────────────────────────────────────────────────────┤
│   KPI 1    KPI 2    KPI 3    KPI 4    KPI 5    KPI 6                │  height 90
│ Persist  Half-life  LR Vol  Opt D/V  Opt WACC  Real Opt             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   2. Brent Price + Cond Vol Time Series (1987-2022)                 │  height 240
│                                                                     │
├─────────────────────┬───────────────────────────────────────────────┤
│                     │                                               │
│  3. Vol Regime      │   7. RISK HEATMAP (THE HEADLINE)              │
│     Distribution    │   Leverage × Vol Regime → PoD                 │  height 320
│                     │                                               │
├─────────────────────┼───────────────────────────────────────────────┤
│                     │                                               │
│  5. WACC Curve      │   8. NPV 2-Way Stress (Brent × WACC)          │  height 200
│     w/ optimum      │                                               │
└─────────────────────┴───────────────────────────────────────────────┘
```

Place sheets 4 (forward cone) and 6 (tax shield) on a secondary tab labeled "GARCH Detail" and "MM Detail" — these are second-order visuals.

---

## Dashboard Actions

1. **Filter from time series**: clicking a year in chart 2 filters charts 3 and 5 to that year's vol regime.
2. **Highlight from heatmap**: clicking a leverage row in chart 7 highlights the matching point on chart 5 (WACC curve).
3. **URL action**: clicking the headline navigates to a dedicated long-form view with annotations.

---

## Theme

- Navy: `#1F3864`
- Green: `#2E7D32` (positive / safe)
- Orange: `#E07A1F` (cautionary / signal)
- Red: `#C00000` (negative / cliff)
- Light backgrounds: `#F5F5F5`
- Yellow highlight: `#FFFF00`
- Amber highlight: `#FFE699`

Font family: Tableau Bold (default). Title font 16pt; sheet titles 12pt; axis 10pt.

---

## Verification Checklist

After build, confirm:

- [ ] **GARCH persistence KPI** shows 0.9930
- [ ] **Optimal D/V KPI** shows 30%
- [ ] **Optimal WACC KPI** shows 8.97%
- [ ] **Real Option Value KPI** shows $681M (or $675M with rounding)
- [ ] **Risk Heatmap cell at D/V=40%, MEDIUM** shows 0.45% (green)
- [ ] **Risk Heatmap cell at D/V=50%, MEDIUM** shows 13.87% (amber)
- [ ] **Risk Heatmap cell at D/V=60%, MEDIUM** shows 62.69% (red)
- [ ] **WACC Curve trough** is at D/V=30% with WACC=8.97%
- [ ] **NPV 2-Way Bear @ 9% WACC** shows ≈ -$840M
- [ ] **NPV 2-Way Bull @ 9% WACC** shows ≈ +$707M
- [ ] **Vol regime distribution** shows LOW≈33%, MED≈34%, HIGH≈28%, CRISIS≈5%
- [ ] All sheets respect the navy/green/orange/red theme
- [ ] Dashboard renders cleanly at 1440×900 with no scrollbars

---

## Methodology Callout (footer text on dashboard)

```
Methodology: GARCH(1,1) Student-t fit to 35.5 years of Brent log-returns (9,010 observations,
1987-2022). Cost of equity from single-factor energy CAPM with Brent as the systematic
risk factor. Capital structure optimization via MM with taxes, levered-beta cost of equity,
and quadratic distress-premium model on debt above D/V=30%. Real Option to Delay computed
from Black-Scholes with σ = GARCH long-run vol (45.83%). Probability of Default from
Merton-style firm-as-call model, asset vol = 55% of commodity vol.

Caveats: EnergyCo financials synthetic, anchored to industry medians for $50B BBB-rated
upstream pure-plays. Beta vs Brent (0.85) industry-typical, not empirically estimated.
Merton PoD assumes log-normal asset values; real default tends to cluster more (jumps,
contagion). Black-Scholes assumes constant σ over option life.
```
