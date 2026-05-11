# Tableau Dashboard Spec — DistributorCo Lean Shield "OEE Drill-Through"

> **Tool:** Tableau Desktop 2023.x or later (NOT Power BI — explicit brief requirement: "Design a Tableau Dashboard").
> **Audience:** Quality VP + Logistics Director + Operations Council
> **Purpose:** Operational control surface for the Lean Six Sigma program. OEE grid is the headline; SPC time-series, EOQ summary, and Control Plan provide drill-through.

---

## 1. Data Sources

Connect Tableau to the seven CSVs in `Module_01/Track_01/lean_shield/outputs/` (or use the SQLite DB `leanshield.db` for a single connection):

| File | Rows | Purpose |
|---|---|---|
| `oee_grid.csv` | 20 | **Headline grid:** 4 modes × 5 markets → OEE |
| `eoq_top10.csv` | 10 | EOQ + Safety Stock per top SKU |
| `control_plan.csv` | 4 | Per-mode SPC control limits and reaction plans |
| `spc_results_Standard_Class.csv` | ~1,100 | Daily X-bar / R / p-late for Standard Class |
| `spc_results_First_Class.csv` | ~1,100 | Daily p-late for First Class |
| `spc_results_Second_Class.csv` | ~1,100 | Daily X-bar / R / p-late for Second Class |
| `spc_results_Same_Day.csv` | ~1,100 | Daily X-bar / R / p-late for Same Day |
| `dashboard_kpis.csv` | 8 | Headline KPIs strip |

For a single connection, the SQLite DB exposes the analytical views directly.

---

## 2. Calculated Fields (Tableau syntax)

```tableau
// --- oee_grid ---
OEE_Pct                = [OEE] * 100
OEE_Bucket             = IF [OEE] < 0.10      THEN "Crisis (<10%)"
                         ELSEIF [OEE] < 0.30  THEN "Poor (10-30%)"
                         ELSEIF [OEE] < 0.50  THEN "Fair (30-50%)"
                         ELSEIF [OEE] < 0.85  THEN "Good (50-85%)"
                                              ELSE "World-class (>85%)" END
Availability_Pct       = [availability] * 100
Performance_Pct        = [performance] * 100
Quality_Pct            = [quality] * 100

// --- eoq_top10 ---
Savings_Pct            = ([annual_savings]) / [current_cost] * 100
ROP_Stockout_Risk      = [reorder_point] - (1.645 * [daily_std] * SQRT([lead_time_days]))

// --- spc_results_<mode> ---
Day_Index              = INDEX()
P_Late_Pct             = [p_late] * 100
Late_Alert             = IIF([p_late] > 0.50, "RED", IIF([p_late] > 0.30, "AMBER", "GREEN"))

// --- control_plan ---
Capability_Status      = [status]
Cpk_Display            = IF ISNULL([Cpk]) THEN "UNDEFINED" ELSE STR(ROUND([Cpk],3)) END
```

---

## 3. Sheet-by-Sheet Build (8 visuals)

### Sheet 1 — `KPI_Strip` (header band)

- **Source:** `dashboard_kpis.csv`
- **Type:** Horizontal text-tile strip
- **Tiles** (left to right, big number on top, label below):
  1. **Firm late rate** → `54.8%` *(red bg)*
  2. **First Class late rate** → `95.3%` *(red bg)*
  3. **Standard Class Cpk** → `0.001` *(amber bg)*
  4. **Second Class Cpk** → `-0.469` *(red bg)*
  5. **Top-10 EOQ savings** → `$50,629` *(green bg)*
  6. **PENDING_PAYMENT bottleneck** → `22.1%` *(amber bg)*
- **Format:** Background navy `#1F3864`. Foreground white.

### Sheet 2 — `OEE_Heatmap` ⭐ **HEADLINE VISUAL** ⭐

- **Source:** `oee_grid.csv`
- **Type:** Heat map (rectangle marks)
- **Rows:** `Shipping Mode` (sorted: Standard Class > Second Class > First Class > Same Day)
- **Columns:** `Market` (LATAM, Europe, Pacific Asia, USCA, Africa)
- **Colour:** `OEE_Pct` — diverging palette
  - 0% → red `#C00000`
  - 27% → amber `#E07A1F`
  - 55% → green `#2E7D32`
- **Labels:** Show `OEE_Pct` formatted as "54.4%"
- **Cell size:** ~140 px × 70 px (boardroom-readable)
- **Title:** "OEE: Shipping Mode × Market (4 × 5 grid, n=180,519 orders)"
- **Tooltip:** "Mode: <Mode>, Market: <Market>, OEE: <OEE_Pct>%, Availability: <Availability_Pct>%, Performance: <Performance_Pct>%, Quality (on-time rate): <Quality_Pct>%, Orders: <orders>"

### Sheet 3 — `SPC_PChart_StdClass` (process control time-series)

- **Source:** `spc_results_Standard_Class.csv`
- **Type:** Line chart with control bands
- **X-axis:** `Day_Index`
- **Y-axis:** `P_Late_Pct`
- **Marks:**
  - Line: navy `#1F3864`
  - Reference lines:
    - Centerline (p̄ = 38.1%) — green dashed
    - UCL = 52.6% — red dashed
    - LCL = 23.6% — red dashed
    - Target = 5% — gold dotted
- **Annotation:** Highlight any subgroup above UCL with a red dot
- **Title:** "Standard Class — Daily Late-Delivery Proportion (n_subgroups ≈ 1,100)"

### Sheet 4 — `SPC_XBar_AllModes` (small-multiples X-bar charts)

- **Source:** Combined SPC files via UNION
- **Type:** 2×2 small-multiples X-bar chart (one per mode)
- **Each panel:** day index on X, daily mean on Y, with centerline + UCL + LCL reference lines
- **Title:** "X-bar Charts — Daily Subgroup Mean Days-to-Ship by Mode"

### Sheet 5 — `EOQ_Summary_Table` (top-10 SKU)

- **Source:** `eoq_top10.csv`
- **Type:** Highlight table
- **Columns:** SKU Name, Annual Demand, EOQ, Safety Stock, ROP, Annual Savings
- **Highlight:** `Annual Savings` with green-shade gradient
- **Sort:** Descending by `total_units` (annual demand)
- **Title:** "EOQ Optimization — Top 10 SKUs (95% Service Level)"

### Sheet 6 — `Pareto_OrderStatus` (the queueing bottleneck visual)

- **Source:** Aggregate from `leanshield.db` view `v_analyze_state_dist`
- **Type:** Combo (bar + line)
- **Bars:** Order count per state, navy
- **Line:** Cumulative percentage, red, with 80% reference line
- **Title:** "Order State Pareto: PENDING_PAYMENT is the Vital Few (22.1%)"

### Sheet 7 — `Control_Plan_Card` (text card with reaction plans)

- **Source:** `control_plan.csv`
- **Type:** Card-style text view (not a chart)
- **Per-mode card:** Process | Cpk | Status | Reaction Plan
- **Colour-coded backgrounds:** red for CRITICAL/DETERMINISTIC, amber for NOT_CAPABLE, green for CAPABLE
- **Title:** "DMAIC Control Plan — Reaction Triggers per Mode"

### Sheet 8 — `Margin_Erosion_BarChart`

- **Source:** Pre-aggregated from `dashboard_kpis.csv` and notebook outputs
- **Type:** Two stacked bars (on-time vs. late, total profit)
- **Y-axis:** Total profit ($M)
- **X-axis:** On-time vs. Late
- **Title:** "Margin Erosion — Profit per Order by Delivery Outcome"

---

## 4. Dashboard Layout (1440 × 900 px)

```
┌──────────────────────────────────────────────────────────────────┐
│  KPI_Strip  (full width, 80 px)                                  │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│        ★ OEE_Heatmap (full width, 280 px) ★                     │
│                                                                  │
├──────────────────────────────────┬───────────────────────────────┤
│ SPC_PChart_StdClass              │ SPC_XBar_AllModes (2x2)       │
│ (50% × 220 px)                   │ (50% × 220 px)                │
├──────────────────────────────────┼───────────────────────────────┤
│ EOQ_Summary_Table                │ Pareto_OrderStatus            │
│ (50% × 200 px)                   │ (50% × 200 px)                │
├──────────────────────────────────┴───────────────────────────────┤
│ Control_Plan_Card (full width, 100 px)                           │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Dashboard Actions

1. **Click on a cell in OEE_Heatmap** → filters all SPC charts and Pareto to that mode + market
2. **Hover on SPC_PChart points** → tooltip shows date, p_late, n in subgroup, any rule violations
3. **Click on a SKU in EOQ_Summary_Table** → drill-through to a separate "SKU Detail" sheet (out of scope for v1, noted as v2)

---

## 6. Theme

| Element | Hex | Usage |
|---|---|---|
| Navy | `#1F3864` | Primary; KPI strip; line charts |
| Green | `#2E7D32` | Positive / capable / on-time |
| Red | `#C00000` | Critical / out-of-spec / late |
| Amber | `#E07A1F` | Marginal / warning |
| Gold | `#FFC000` | Optimal target / reference |
| Light-blue | `#D9E2F3` | Section headers |
| Charcoal | `#333333` | Body text |
| Off-white | `#F5F5F0` | Sheet background |

Font: Tableau Sans. Titles 14 pt bold. KPI numbers 28 pt bold.

---

## 7. Verification Checklist

After publishing:

| Visual | Cell / Marker | Expected Value | ✓ |
|---|---|---|---|
| KPI_Strip | Firm late rate | `54.8%` | ☐ |
| KPI_Strip | First Class late rate | `95.3%` | ☐ |
| KPI_Strip | Standard Class Cpk | `0.001` | ☐ |
| KPI_Strip | Second Class Cpk | `-0.469` | ☐ |
| KPI_Strip | Top-10 savings | `$50,629` | ☐ |
| OEE_Heatmap | Standard Class / LATAM | `54.4%` | ☐ |
| OEE_Heatmap | Same Day / Africa | `0.0%` | ☐ |
| OEE_Heatmap | First Class (any market) | `1.5–2.6%` | ☐ |
| SPC_PChart_StdClass | p̄ centerline | `38.1%` | ☐ |
| SPC_PChart_StdClass | UCL | `52.6%` | ☐ |
| EOQ_Summary | Total savings | `$50,629` | ☐ |
| Pareto | PENDING_PAYMENT share | `22.1%` | ☐ |

---

## 8. Methodology Callout (top-right of dashboard)

> **Methodology.** SPC limits computed via X-bar/R formulas (Montgomery, *Introduction to Statistical Quality Control*) using daily subgroups of n ≈ 5–15 orders per mode-day. p-charts use binomial 3σ control limits. Cp/Cpk computed against scheduled-days as USL, zero as LSL. EOQ via classical Wilson formula with 20% holding cost rate and $50 order cost; Safety Stock at 95% service level (Z = 1.645). OEE = Availability × Performance × Quality with industry-standard component definitions. **DistributorCo financials are synthetic, anchored to dataset scale; per-order numbers are real but firm-level revenue ($1.2B) and SKU-count narration (12K) are scaled for boardroom relevance.**
