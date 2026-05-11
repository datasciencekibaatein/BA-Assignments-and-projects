# GroceryCo Operational Health — Tableau Dashboard Spec

**Source data:** `dashboard_extract.csv` (single connection — has everything)
**Optional secondary:** `aisle_drilldown.csv` (for the worst-offender drill-down panel)

The transformation SQL has already done all the math. Tableau's job is **plotting only** — no LOD calcs, no fancy table calcs, no statistical functions. If you find yourself writing a complex calculated field, something went wrong upstream.

---

## Connection Setup

1. **Open Tableau Desktop / Tableau Public**
2. Connect → Text File → select `dashboard_extract.csv`
3. (Optional) Add a second connection to `aisle_drilldown.csv`. Do NOT join them in the data model — keep them as separate data sources, switch via dashboard actions instead. (Joining them would explode rows since aisles have no week_id.)
4. Field types to verify after import:
   - `week_id`, `n_items`, `weeks_below_lcl`, `weeks_above_ucl`, `weeks_ooc_total` → integer
   - `reorder_rate`, `centerline/ucl/lcl/uwl/lwl/sigma_hat`, `z_score`, `dept_mean`, `gap_vs_platform`, `t_stat`, `p_value_approx`, `weekend_share` → number (decimal)
   - `department`, `spc_status`, `leakage_flag` → string (dimension)

---

## Calculated Fields (only 3, all simple)

```
[SPC Color]               IF CONTAINS([spc_status], "Red")  THEN "Red" ELSEIF CONTAINS([spc_status], "WA") THEN "Yellow"

ELSE "Green"
END

[Leakage Color]           CASE [leakage_flag]
                              WHEN "LEAKAGE_CONFIRMED" THEN "Red"
                              WHEN "LEAKAGE_SUSPECTED" THEN "Amber"
                              WHEN "OVERPERFORMER"     THEN "Blue"
                              ELSE "Grey"
                          END

[Significance Marker]     IF [p_value_approx] < 0.001 THEN "***"
                          ELSEIF [p_value_approx] < 0.01  THEN "**"
                          ELSEIF [p_value_approx] < 0.05  THEN "*"
                          ELSE "ns" END
```

That's it. Everything else is handled in the SQL.

---

## Sheets to build

### Sheet 1 — `SPC_DeptControlChart`  (THE main chart)

The brief asked for "per-department SPC control charts (mean reorder rate ± 3σ, weekly observations)."

| Shelf | Field | Notes |
|---|---|---|
| Columns | `week_id` (continuous) | weekly subgroups |
| Rows | `reorder_rate` (avg) | the X-bar |
| Rows | `centerline`, `ucl`, `lcl`, `uwl`, `lwl` | dual axis these as reference lines (see below) |
| Color | `[SPC Color]` | red/amber/green |
| Detail | `department` | one chart per department via "Trellis" — see Filters below |
| Filter | `department` (Show Filter, multi-select dropdown) | drives the small-multiples panel |
| Filter | `week_id` (range slider) | optional time-window filter |

**Reference lines (use Analytics pane, NOT calc fields):**
- Constant lines for UCL (red dashed), LCL (red dashed), centerline (black solid), UWL/LWL (orange dotted). Pull values from Avg([ucl]), Avg([lcl]) etc. — they're constant per row anyway.

**Mark type:** Line + Circle (so out-of-control points stand out as red dots on the line)
**Tooltip:**
```
Department: <department>
Week: <week_id>
Reorder rate: <reorder_rate> (z = <z_score>)
Status: <spc_status>
n_items in subgroup: <n_items>
```

### Sheet 2 — `LeakageReport`  (highlight table)

The brief asked for "a Reorder Leakage report listing departments operating below the lower control limit, each annotated with its t-test p-value vs platform mean."

| Shelf | Field |
|---|---|
| Rows | `department` (sort by `gap_vs_platform` ascending → worst at top) |
| Columns | Measure Names (filtered to: `dept_mean`, `gap_vs_platform`, `weeks_below_lcl`, `t_stat`, `p_value_approx`) |
| Text | Measure Values |
| Color | `[Leakage Color]` |
| Filter | `leakage_flag` ≠ "STABLE" (or Top N by `gap_vs_platform` ascending — pick 10) |

Add `[Significance Marker]` as a separate text column to the right of `p_value_approx` so users immediately see the * / ** / *** stars.

**Number formatting:**
- `dept_mean`, `gap_vs_platform` → percentage, 2 decimals
- `t_stat` → number, 2 decimals
- `p_value_approx` → scientific or "<0.001" custom format

### Sheet 3 — `AisleDrillDown`  (bar chart, secondary data source)

| Shelf | Field |
|---|---|
| Rows | `aisle` (sorted by `aisle_reorder_rate` ascending) |
| Columns | `aisle_reorder_rate` (avg) |
| Color | `aisle_flag` ("WORST" red, "WEAK" amber, "OK" grey) |
| Detail/Filter | `department` |

**Reference line** at platform mean (constant from `[platform_mean]`).
**Filter action target** — gets activated by clicking a department on Sheet 2.

### Sheet 4 — `PlatformKPIs`  (header strip)

Single-row "BAN" cards (Big Ass Numbers):

- Platform mean reorder rate → `centerline` (avg)
- Departments out of control → COUNTD(IF [leakage_flag] CONTAINS "LEAKAGE" THEN [department] END)
- Total weekly subgroups → COUNTD([week_id]) × COUNTD([department])
- Weeks below LCL across platform → SUM([weeks_below_lcl]) (use `Aggregate by Department` calc since the field repeats across weeks: `{ FIXED [department] : MAX([weeks_below_lcl]) }` summed)

Format each as size-36 bold text on a colored card.

### Sheet 5 — `WeekendVsWeekday`  (t-test result strip)

A single-row text card showing the result of the t-test from Notebook 04. Hardcode the values pulled from `outputs/ttest_results.csv` (these are conclusions, not data Tableau needs to recompute):

```
WEEKEND vs WEEKDAY: basket size +0.42 items (p < 0.001) — significant
WEEKEND vs WEEKDAY: reorder rate +0.014   (p = 0.003)   — significant
MORNING vs EVENING: basket size +0.05 items (p = 0.71)  — NOT significant ← negative control
```

Use a Caption sheet (Worksheet → Show Title, hide marks). Or just a text object on the dashboard.

---

## Dashboard layout (1400 × 900 px)

```
┌─────────────────────────────────────────────────────────────────────┐
│  GroceryCo Operational Health Audit                          [Logo] │  ← Title (h=60)
├─────────────────────────────────────────────────────────────────────┤
│  [PlatformKPIs strip — 4 BANs side by side]                         │  ← h=80
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  SPC_DeptControlChart (small multiples)                             │  ← h=480 (main)
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐    │
│  │ frozen      │ │ other       │ │ missing     │ │ produce     │    │
│  │ ⎯⎯⎯⎯⎯⎯⎯⎯⎯ UCL│ │             │ │             │ │             │    │
│  │ ●●●●●●●     │ │             │ │             │ │             │    │
│  │ ⎯⎯⎯⎯⎯⎯⎯⎯⎯ LCL│ │             │ │             │ │             │    │
│  │ ● ← red     │ │             │ │             │ │             │    │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘    │
│  (4×N grid based on dept filter)                                    │
├──────────────────────────────────┬──────────────────────────────────┤
│                                   │                                  │
│  LeakageReport (highlight table)  │  AisleDrillDown                 │  ← h=320
│  Worst departments + p-values     │  Bars per aisle within selected │
│                                   │  department                      │
│                                   │                                  │
├──────────────────────────────────┴──────────────────────────────────┤
│  WeekendVsWeekday (t-test text strip)                               │  ← h=40
└─────────────────────────────────────────────────────────────────────┘
```

---

## Dashboard actions (the interactivity)

1. **Filter action: LeakageReport → AisleDrillDown**
   - Source: Sheet 2 (LeakageReport), select on row
   - Target: Sheet 3 (AisleDrillDown), filter on `department`
   - Run on: Select
   - Clearing: "Show all values"

2. **Filter action: LeakageReport → SPC_DeptControlChart**
   - Source: Sheet 2, select on row
   - Target: Sheet 1, filter on `department`
   - Run on: Select
   - Effect: clicking a leaky department zooms the SPC chart to just that one (large single chart instead of small multiples)

3. **Highlight action: SPC_DeptControlChart → LeakageReport**
   - Source: Sheet 1, hover on point
   - Target: Sheet 2, highlight `department`
   - Effect: hovering an SPC dot highlights its row in the leakage table

---

## Color palette

Use a custom workbook palette (`Format → Workbook → Colors`):
- Red:    `#C00000` (out of control, leakage confirmed)
- Amber:  `#E07A1F` (warning zone, leakage suspected)
- Green:  `#5B8E3D` (in control, stable)
- Blue:   `#1F3864` (overperformer, lines/markers)
- Grey:   `#7F7F7F` (background dept lines, neutral text)

Match these to the Notebook 03/04 figure palette so the deck and dashboard look like one product.

---

## Performance notes

- `dashboard_extract.csv` for our synthetic 5K-order test was 41 KB / 146 rows. Production (131K orders) will be roughly 21 depts × ~1500 weeks = ~30K rows, ~5 MB. Tableau handles that without an extract — but extract anyway (Tableau Hyper format) for the screenshot performance.
- `aisle_drilldown.csv` is small (~30 rows × top-5 depts = ~150 rows). No optimization needed.
- If you need to filter by time of day or weekend/weekday, those fields are NOT in `dashboard_extract.csv` (they're per-order, would explode the table). Build a separate small aggregation in SQL first if needed.

---

## What NOT to do in Tableau

- ❌ Don't compute control limits via WINDOW_AVG / WINDOW_STDEV — already in the CSV.
- ❌ Don't compute z-scores via table calcs — already in the CSV.
- ❌ Don't try to compute the t-test in Tableau — p-values are precomputed in `leakage_report.csv` and exact (Welch's) values come from `ttest_results.csv` (Notebook 04).
- ❌ Don't join `dashboard_extract` to `aisle_drilldown` in the data model — different grain, will duplicate. Keep separate, link via dashboard actions.

---

## Publishing

1. File → Save As → `GroceryCo_Audit.twbx` (packaged workbook — bundles the CSVs)
2. To Tableau Public: File → Save to Tableau Public As… (free hosting, public link)
3. To Tableau Server / Cloud: Server → Publish Workbook…

Estimated build time from CSVs to published dashboard: **30–45 minutes**.
