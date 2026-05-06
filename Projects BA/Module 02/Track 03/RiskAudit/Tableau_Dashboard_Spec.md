# Tableau Dashboard Build Spec — Project Risk Audit

The Excel financial engine handles the math; this dashboard makes it interactive for the CFO. Build time in Tableau Desktop or Tableau Public is approximately 30 minutes following these steps.

---

## 0. Files you need

All produced by the analytics notebook in `outputs/`:

| File | Use |
|---|---|
| `tableau_npv_extract.csv` | Main data source — 110 rows of (Project, WACC, Elasticity, NPV) for the heatmap |
| `tableau_scenario_summary.csv` | The 6-row table (3 scenarios × 2 projects) for the scenario-toggle KPI cards |
| `industrials_returns_panel.csv` | 2,768-row sector return distribution for the risk histogram |
| `cat_financial_panel.csv` | CAT 5-year financials for the trend chart |
| `cat_fcf_forecast.csv` | 10-year FCF forecast for the projection chart |

---

## 1. Connect Data Sources

**Open Tableau Desktop → Connect → Text File**

Connect each CSV in turn. Tableau will auto-detect column types correctly for these files.

After connecting, in the **Data Source** view, set the data sources to **Live** (not Extract) so the dashboard refreshes when the notebook regenerates the CSVs.

**Critical:** No relationships needed between data sources — each chart uses one source.

---

## 2. Calculated Fields (create in Tableau)

In the main `tableau_npv_extract` source:

```
[NPV ($M)]            = [NPV Millions]
[NPV Status]          = IF [NPV Millions] > 0 THEN "Positive" ELSE "Negative" END
[Project Color]       = IF [Project] = "Domestic" THEN "Automate" ELSE "Outsource" END
[WACC Display]        = STR([WACC Pct]) + "%"
[Elasticity Display]  = "Elasticity = " + STR([Elasticity])
```

In `tableau_scenario_summary`:

```
[Recommendation Color] = IF [Recommendation] = "PROCEED" THEN "green" ELSE "red" END
[NPV Display]          = "$" + STR(ROUND([NPV Millions])) + "M"
[IRR Display]          = STR(ROUND([IRR Pct], 1)) + "%"
```

In `industrials_returns_panel`:

```
[Return Bucket] = IF [Annual Return Pct] < -50 THEN "<-50% (severe loss)"
                  ELSEIF [Annual Return Pct] < -20 THEN "-50% to -20%"
                  ELSEIF [Annual Return Pct] < 0 THEN "-20% to 0%"
                  ELSEIF [Annual Return Pct] < 20 THEN "0% to 20%"
                  ELSEIF [Annual Return Pct] < 50 THEN "20% to 50%"
                  ELSE ">50% (high gain)" END
```

---

## 3. Build the Sheets

### Sheet 1 — NPV Heatmap (the centerpiece)

- **Source:** `tableau_npv_extract`
- **Visual:** Heatmap (custom from Show Me → highlight table)
- **Columns:** `WACC Pct` (discrete dimension)
- **Rows:** `Elasticity` (discrete dimension, sort descending)
- **Filter:** `Project` — single-select (default = Domestic)
- **Color:** `NPV Millions` — diverging scale, red → yellow → green, midpoint at zero
- **Label:** `NPV Millions` formatted as "$#,##0M"
- **Tooltip:** Project, WACC, Elasticity, NPV, NPV Status

### Sheet 2 — Project NPV Comparison (line chart)

- **Source:** `tableau_npv_extract`
- **Visual:** Line chart
- **Columns:** `WACC Pct`
- **Rows:** `NPV Millions`
- **Filter:** `Elasticity` — single-select slider (default = 0)
- **Color:** `Project` (Domestic = navy `#1F3864`, Outsource = orange `#E07A1F`)
- **Reference line:** `Y = 0` (horizontal black line — the NPV breakeven)
- **Annotation:** Mark the cross-over point manually (~10.5% WACC) with a vertical dashed line

### Sheet 3 — Scenario KPI Cards (the executive scorecard)

- **Source:** `tableau_scenario_summary`
- **Visual:** Discrete cards (one card per Project × Scenario combination = 6 cards)
- **Layout:** Use a Container with 6 cells in a 2×3 grid
- **Card fields:** Project name, NPV ($M), IRR (%), Recommendation
- **Color rule:** Green background if Recommendation = "PROCEED"
- **Filter:** `Scenario` — single-select with ALL option (default = "Base Case")

### Sheet 4 — Sector Return Distribution Histogram

- **Source:** `industrials_returns_panel`
- **Visual:** Histogram
- **Columns:** `Annual Return Pct` (binned, bin size = 10%)
- **Rows:** `COUNT(Annual Return Pct)`
- **Reference lines:**
  - Mean: 7.36% (vertical, color red)
  - Mean + 1σ: 54.54% (vertical, color orange, dashed)
  - Mean - 1σ: -39.82% (vertical, color orange, dashed)
- **Title:** "Industrials Sector Returns: n = 2,768, μ = 7.36%, σ = 47.18%"
- **Tooltip:** Bucket, count, share of total

### Sheet 5 — CAT Historical Financials

- **Source:** `cat_financial_panel`
- **Visual:** Combo chart (bar + line)
- **Columns:** `year`
- **Rows (left axis):** `Revenue` as bars (in $B, divide by 1e9)
- **Rows (right axis):** `Free CF` as line (in $B)
- **Annotation:** Highlight 2016 ("commodity-cycle trough")

### Sheet 6 — CAT 10-Year FCF Forecast

- **Source:** `cat_fcf_forecast`
- **Visual:** Line chart with confidence band
- **Columns:** `year`
- **Rows:** `Base Case 2 5pct` as solid line, `Low Growth 1pct` and `High Growth 4pct` as fill area
- **Color:** Green band between Low and High, navy line for Base
- **Title:** "10-Year FCF Forecast — Base case ±growth scenario band"

---

## 4. Assemble the Dashboard

**File → Dashboard → New Dashboard**, size = 1280×800.

Layout:

```
+------------------------------------------------------------------+
| TITLE: Project Risk Audit — Capital Deployment & Macro Stress    |
| Subtitle: Caterpillar (CAT) anchor | 200-employee R&D plant      |
+------------------------------------------------------------------+
|  SCENARIO TOGGLE BAR (3 buttons: Low Growth | Base | High Infl)  |
+----------------------------+-------------------------------------+
|                            |                                     |
|  Sheet 3: KPI Cards        |  Sheet 1: NPV Heatmap              |
|  (6 cards, 2×3 grid)       |  (Project filter applies here)     |
|                            |                                     |
+----------------------------+-------------------------------------+
|                            |                                     |
|  Sheet 2: NPV Lines        |  Sheet 4: Return Distribution      |
|                            |                                     |
+----------------------------+-------------------------------------+
|                            |                                     |
|  Sheet 5: CAT History      |  Sheet 6: FCF Forecast             |
|                            |                                     |
+----------------------------+-------------------------------------+
| Filters: [Scenario] [Project] [Elasticity slider]                |
+------------------------------------------------------------------+
```

---

## 5. Dashboard Actions (the "CFO toggle" the brief asks for)

This is the key interactive feature. Add three actions via **Dashboard → Actions**:

### Action 1: Filter Scenario

- **Type:** Filter
- **Source sheet:** Sheet 3 (KPI Cards)
- **Target sheets:** All other sheets
- **Run on:** Select
- **Source field:** `Scenario`
- **Effect:** Clicking a scenario card filters every chart to that scenario's WACC

### Action 2: Highlight Project

- **Type:** Highlight
- **Source sheet:** Sheet 2 (NPV Lines)
- **Target sheets:** Sheets 1, 3
- **Run on:** Hover
- **Source field:** `Project`
- **Effect:** Hovering a project line highlights its data everywhere

### Action 3: Reset Filters Button

- Add a **Button** object to the dashboard (Dashboard → Object → Button)
- **Action:** Navigate to dashboard → reset
- **Label:** "Reset View"

---

## 6. Verification Checklist

Before publishing:

- [ ] **NPV Heatmap (Sheet 1):** Top-left cell (WACC=5%, Elasticity=0) shows ~$1,467M for Domestic
- [ ] **NPV Lines (Sheet 2):** Lines cross at ~10.5% WACC (Domestic = Outsource)
- [ ] **KPI Cards (Sheet 3):** Base Case Domestic shows NPV ~$1,036M, IRR 16.39%
- [ ] **KPI Cards (Sheet 3):** High Inflation Domestic shows NPV ~$433M (lower because WACC is 12%)
- [ ] **Histogram (Sheet 4):** Center of mass around +7%, long right tail visible
- [ ] **CAT History (Sheet 5):** 2016 trough visible (Net Income negative, Revenue dip)
- [ ] **FCF Forecast (Sheet 6):** Base case starts at ~$4.2B (median FCF) in 2019, grows to ~$5.4B by 2028
- [ ] **Scenario actions work:** Click "High Inflation" KPI card → all other sheets update to WACC = 12%

---

## 7. Theme

Use a clean financial-industry palette throughout:

| Element | Color |
|---|---|
| Title bar | Navy `#1F3864` |
| Domestic project | Navy `#1F3864` |
| Outsource project | Orange `#E07A1F` |
| Positive NPV | Green `#2E7D32` |
| Negative NPV | Red `#C00000` |
| Background | White |
| Body text | Dark grey `#333333` |
| Font | Calibri (Tableau default works fine) |

---

## 8. Publish & Export

**For Meritshot delivery:** keep as `.twbx` (packaged workbook with embedded data).

**For client demo:** publish to Tableau Public (free) at `public.tableau.com` and embed the link in the deck.

**For static export:** Dashboard → Export → Image → PNG (good for slide decks where interactivity is unnecessary).

---

## Appendix — Methodology callout to embed in dashboard

Add as a text caption in the bottom-right corner so the methodology is visible on every page:

> **Methodology.** Anchor company: Caterpillar Inc. (CAT). FCF forecast uses median 5-year baseline + explicit growth scenarios (cyclical-aware). Risk distribution uses cross-sectional σ of 2,768 ticker-year returns from Industrials sector (2014-2018). WACC = rf + β·ERP, with ERP scaled 0.7×/1.0×/2.0× across the three scenarios. Cross-over WACC ≈ 10.5%.
