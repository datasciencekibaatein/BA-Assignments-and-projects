# Tableau Dashboard Build Spec — Automation Risk Heatmap

This dashboard turns the GARCH + Monte Carlo notebook outputs into an interactive risk dashboard for the CFO. Build time in Tableau Desktop or Tableau Public is approximately 35 minutes.

---

## 0. Files you need

All produced by the analytics notebook in `outputs/`:

| File | Use |
|---|---|
| `tableau_pod_extract.csv` | **Primary data source** — 35 cells (5 demand × 7 WACC) with PoD, 95% CI, mean NPV, P5 NPV, risk band |
| `tableau_npv_paths.csv` | **NPV-distribution data** — 60K rows of (path × cell) NPV for the violin/histogram plot |
| `pod_grid.csv` | Pre-aggregated PoD heatmap |
| `mean_npv_grid.csv` | Pre-aggregated mean NPV heatmap |
| `pod_with_ci.csv` | PoD with bootstrap CIs (used in tooltips) |
| `dashboard_kpis.csv` | Headline KPIs |

---

## 1. Connect Data Sources

**Open Tableau Desktop → Connect → Text File**

Connect each CSV in turn. Tableau auto-detects column types. Set each source to **Live** so the dashboard refreshes when the notebook regenerates.

No data-source relationships needed — each chart uses one CSV.

---

## 2. Calculated Fields (in `tableau_pod_extract`)

```
[PoD %]            = AVG([Pod Pct])
[CI Width]         = AVG([Ci High Pct]) - AVG([Ci Low Pct])
[CI Range Display] = "[" + STR(ROUND([Ci Low Pct],1)) + "%, " + STR(ROUND([Ci High Pct],1)) + "%]"
[Mean NPV Color]   = IF [Mean Npv M] > 0 THEN "Profit" ELSE "Loss" END
[Decision]         = IF [Pod] < 0.30 THEN "ACCEPT"
                      ELSEIF [Pod] < 0.50 THEN "PROCEED WITH CAUTION"
                      ELSE "REJECT" END
```

In `tableau_npv_paths`:

```
[NPV in $M]        = AVG([Npv M])
[Default Flag]     = AVG([Default])  // 0 to 1 share of paths
```

---

## 3. Build the Sheets

### Sheet 1 — Executive KPI Strip

- **Source:** `dashboard_kpis`
- **Visual:** 6 large-number tiles in a row
- **Tiles:** 
  - Base-case NPV (deterministic) — green if positive
  - Base-case PoD — red if >50%
  - Brief stress NPV — colored by sign
  - Brief stress PoD — colored
  - GARCH persistence (0.993)
  - Long-run vol (45.83%)

### Sheet 2 — Probability of Default Heatmap (THE HERO CHART)

- **Source:** `tableau_pod_extract`
- **Visual:** Highlight table
- **Columns:** `Wacc Label`
- **Rows:** `Demand Label`
- **Color:** `PoD %`, sequential white-to-red
- **Label:** PoD% as the primary number, CI range below in smaller font
- **Tooltip:** Mean NPV, P5 NPV, PoD, CI low, CI high, decision recommendation
- **Title:** "Probability of Default by WACC × Demand Shock — 10,000 GARCH-driven Monte Carlo paths"

### Sheet 3 — Mean NPV Heatmap

- **Source:** `tableau_pod_extract`
- **Visual:** Highlight table
- **Columns:** `Wacc Label`
- **Rows:** `Demand Label`
- **Color:** `Mean NPV M`, diverging red→yellow→green centered at 0
- **Label:** Mean NPV in $M
- **Title:** "Expected NPV ($M) by WACC × Demand Shock"

### Sheet 4 — NPV Distribution Violin/Histogram

- **Source:** `tableau_npv_paths`
- **Visual:** Box plot or histogram
- **Columns:** `Wacc Label` (filter to selected scenarios)
- **Rows:** `NPV in $M`
- **Color:** `Default Flag` (red for default, green for profit)
- **Reference line:** Y = 0 (the default boundary)
- **Filter:** Allow user to flip between demand shock levels via parameter
- **Title:** "NPV Distribution — 10,000 paths show the fat-tail downside"

### Sheet 5 — Confidence Interval Plot

- **Source:** `tableau_pod_extract`
- **Visual:** Dot plot with horizontal CI bars
- **Columns:** `PoD Pct` (with min/max from CI columns as error bars)
- **Rows:** Combination of `Wacc Label` + `Demand Label`
- **Color:** Risk band
- **Reference line:** X = 50% (coin-flip threshold)
- **Title:** "PoD with 95% Bootstrap Confidence Intervals"

### Sheet 6 — GARCH Diagnostics Embed

- **Source:** None (embed PNG image as a Dashboard object)
- Embed `figures/brent_audit.png` and `figures/garch_forecast_cone.png` side by side

### Sheet 7 — Summary Recommendation Table

- **Source:** `tableau_pod_extract`
- **Visual:** Text table
- **Filter:** Pre-set 4 named scenarios (Baseline, Rate Shock, Demand Shock, Combined Stress)
- **Columns:** Mean NPV, PoD, CI Low, CI High, Decision
- **Title:** "Headline scenarios — what the CFO needs to see"

---

## 4. Assemble the Dashboard

**File → Dashboard → New Dashboard**, size = 1440 × 900.

Layout:

```
+-----------------------------------------------------------------------+
| TITLE: $150M Automation Risk Audit — GARCH-Driven Monte Carlo         |
+-----------------------------------------------------------------------+
| Sheet 1: 6 KPI tiles                                                  |
+-----------------------------+----------------------------------------+
| Sheet 2: PoD Heatmap        | Sheet 3: Mean NPV Heatmap              |
| (THE HERO)                  |                                        |
+-----------------------------+----------------------------------------+
| Sheet 4: NPV Distribution   | Sheet 5: PoD with CIs (dot plot)       |
+-----------------------------+----------------------------------------+
| Sheet 6: GARCH Diagnostics  | Sheet 7: Recommendation Table          |
+-----------------------------+----------------------------------------+
| Filters: [Demand Shock] [WACC]                                        |
+-----------------------------------------------------------------------+
```

---

## 5. Dashboard Actions

### Action 1: "Drill from heatmap to distribution" (Filter)
- **Source:** Sheet 2 (PoD Heatmap)
- **Target:** Sheet 4 (NPV Distribution)
- **Run on:** Select
- **Source fields:** `Wacc Label`, `Demand Label`
- **Behavior:** Click any cell in the PoD heatmap → distribution sheet shows just those 10K paths

### Action 2: "Highlight on hover"
- **Source:** All
- **Target:** All
- **Run on:** Hover
- **Source field:** `Wacc Label`

### Action 3: "Reset View"
- Standard reset button

---

## 6. Verification Checklist

Before publishing, verify these numbers match the notebook:

- [ ] **Sheet 1:** Base PoD = **50.1%**, Brief stress PoD = **63.6%**
- [ ] **Sheet 2:** Cell at WACC=10%, Demand=0% shows **50.1%** PoD
- [ ] **Sheet 2:** Cell at WACC=12%, Demand=-15% shows **63.6%** PoD (the brief stress)
- [ ] **Sheet 2:** Worst cell (WACC=14%, Demand=-20%) shows **75.7%** PoD
- [ ] **Sheet 3:** Cell at WACC=10%, Demand=0% shows mean NPV **-$66M** (negative because of fat-tail dominance)
- [ ] **Sheet 5:** All CI widths around **±1pp** (from 1000 bootstrap resamples)

---

## 7. Theme

| Element | Color |
|---|---|
| Title bar | Navy `#1F3864` |
| KPI good values | Green `#2E7D32` |
| KPI critical values | Red `#C00000` |
| Profit (NPV>0) | Green `#2E7D32` |
| Default (NPV<0) | Red `#C00000` |
| Background | White |
| Body text | `#333333` |
| Font | Calibri / Tableau default |

---

## Appendix — Methodology callout

Add as a text caption:

> **Methodology.** GARCH(1,1) with Student-t residuals fitted to 9,010 daily Brent log-returns (1987-2022). Persistence (α+β) = 0.993; half-life of vol shocks = 99 days; long-run annualised vol = 45.83%. 10,000 Monte Carlo paths × 10-year horizon. Oil multipliers capped at [0.10x, 5.00x] for economic plausibility. PoD = share of paths where project NPV < 0. 95% CIs from 1,000 bootstrap resamples. IndustrialCo financial baseline: $1B revenue, 60% gross margin, 8% energy/COGS, $150M capex, $28M Y1 labor savings.
