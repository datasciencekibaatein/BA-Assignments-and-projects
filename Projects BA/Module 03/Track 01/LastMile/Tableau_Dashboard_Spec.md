# Tableau Dashboard Build Spec — Last-Mile Delivery Audit

This dashboard turns the analytics notebook outputs into an interactive executive view with the **drill-through** action the brief explicitly asks for. Build time in Tableau Desktop or Tableau Public is approximately 35 minutes following these steps.

---

## 0. Files you need

All produced by the analytics notebook in `outputs/`:

| File | Use |
|---|---|
| `tableau_orders_master.csv` | **Primary data source** — 65,752 orders with full hierarchy (Market → Region → Country → Mode → Order ID) |
| `oee_by_mode.csv` | OEE scorecard by Shipping Mode (the brief's complex-join output) |
| `late_rate_by_region.csv` | 23 regions with late-rate, n, mean shipping days |
| `mode_significance_tests.csv` | p-values per Shipping Mode |
| `sarima_forecast_forward.csv` | 90-day forward volume forecast with 95% CI |
| `sarima_forecast.csv` | Backtest forecast vs actuals |
| `spc_pchart_by_mode.csv` | Weekly p-chart data, broken out by Shipping Mode |
| `dashboard_kpis.csv` | The 6 headline KPIs for the top of the dashboard |

---

## 1. Connect Data Sources

**Open Tableau Desktop → Connect → Text File**

Connect each CSV in turn. Tableau will auto-detect column types correctly. Set each source to **Live** (not Extract) so the dashboard refreshes when the notebook regenerates the CSVs.

**Important:** No data-source relationships needed — each chart uses one CSV. The drill-through hierarchy lives inside `tableau_orders_master.csv` and is built using Tableau's native Hierarchy feature (Step 2.2 below).

---

## 2. Calculated Fields & Hierarchy (in `tableau_orders_master`)

### 2.1 Calculated fields

```
[Late Delivery Rate]    = AVG([Late Delivery Risk])
[Schedule Variance Days]= AVG([Days Shipping Real]) - AVG([Days Shipping Sched])
[Is Late]               = IF [Late Delivery Risk] = 1 THEN 1 ELSE 0 END
[OEE Quality Score]     = 1 - AVG([Late Delivery Risk])
[Late Severity]         = IF [Variance Days] >= 3 THEN "Severe (3d+)"
                          ELSEIF [Variance Days] >= 1 THEN "Moderate (1-3d)"
                          ELSEIF [Variance Days] = 0  THEN "On-Time"
                          ELSE "Early" END
[Profit Color]          = IF [Order Profit] < 0 THEN "Loss" ELSE "Profit" END
```

### 2.2 The drill-through hierarchy (this is the brief's Task 4 explicitly)

In the Data pane, **drag** these dimensions onto each other to create the hierarchy:

```
Geographic Drill-Through
├── Market Name           (top level: 5 markets)
├── Region Name           (23 regions)
├── Destination Country   (164 countries)
└── Order ID              (row-level)
```

Then for the operational drill-through:

```
Operational Drill-Through
├── Shipping Mode         (top level: 4 modes)
├── Customer Segment      (Consumer/Corporate/Home Office)
└── Order ID              (row-level)
```

Tableau's `+` icons on the dashboard will let the executive expand from Market down to specific Order IDs.

---

## 3. Build the Sheets

### Sheet 1 — Executive Scorecard (the headline strip)

- **Source:** `dashboard_kpis`
- **Visual:** 6 large-number KPI tiles in a horizontal row
- **Tiles:** Total Orders | Late Delivery Rate (highlighted red if >40%) | Mean Shipping Days | Mean Schedule Days | Mean Schedule Variance | Total Profit
- **Format:** Large bold numbers, small muted captions
- **Conditional color:** Late Delivery Rate cell — green if <30%, amber if 30-50%, red if >50% (it will be red in our data, ~55%)

### Sheet 2 — OEE Scorecard by Shipping Mode (the audit's hero finding)

- **Source:** `oee_by_mode`
- **Visual:** Horizontal bar chart with 3-column matrix overlay
- **Rows:** `Mode Name`
- **Columns:** Three measures side-by-side: `Availability`, `Performance`, `Quality`, then `OEE`
- **Color:** Diverging green→red, OEE column is the focus
- **Sort:** Descending by OEE
- **Annotations:** Mark the SLA on the side ("Standard: 4d", "First: 1d", etc.)

### Sheet 3 — Late Delivery Rate Heatmap (Market × Mode)

- **Source:** `tableau_orders_master`
- **Visual:** Highlight table
- **Columns:** `Shipping Mode`
- **Rows:** `Market Name`, then `Region Name` (drill-through enabled)
- **Color:** `Late Delivery Rate`, diverging red→green inverted (red = high late rate)
- **Label:** Late rate as percentage, with order count below in smaller font
- **Filter:** None at this level; the dashboard filters apply

### Sheet 4 — SARIMA 90-Day Forecast (capacity planning)

- **Source:** `sarima_forecast_forward`
- **Visual:** Line chart with confidence band
- **Columns:** `Date`
- **Rows:** `Forecast` (line), `Lower 95` and `Upper 95` (bands)
- **Color:** Forecast line navy `#1F3864`, CI band light navy 20% opacity
- **Reference line:** Historical mean as dashed grey horizontal
- **Title:** "90-Day Volume Forecast — total expected orders: [SUM(forecast)]"
- **Annotation:** "MAE 0.75 orders/day | MAPE 1.09% (validated on 90-day holdout)"

### Sheet 5 — P-Chart by Shipping Mode (SPC, Task 3)

- **Source:** `spc_pchart_by_mode`
- **Visual:** Small-multiples line chart (4 panels — one per mode)
- **Columns:** `Week Start`
- **Rows:** `P` (the late rate)
- **Reference lines per panel:** UCL (red dashed), LCL (red dashed), p-bar (green solid)
- **Marks:** Red X for `OOC = TRUE` weeks
- **Filter:** `Mode` becomes the small-multiple grouping
- **Title:** "Weekly Late-Rate P-Chart by Shipping Mode (3σ control limits)"

### Sheet 6 — Variance Distribution by Mode

- **Source:** `tableau_orders_master`
- **Visual:** Box plot
- **Columns:** `Shipping Mode`
- **Rows:** `Variance Days`
- **Reference line:** Y = 0 (the SLA target)
- **Color:** by mode
- **Title:** "Schedule Variance — actual minus scheduled days, by mode"

### Sheet 7 — The Drill-Through Detail Table (this is the brief's Task 4)

- **Source:** `tableau_orders_master`
- **Visual:** Detail table (text table)
- **Rows:** `Order ID`, `Order Date`
- **Columns:** `Market Name`, `Region Name`, `Destination Country`, `Shipping Mode`, `Days Shipping Real`, `Days Shipping Sched`, `Variance Days`, `Late Severity`, `Customer Segment`, `Order Profit`
- **Filter:** This sheet is **filtered by every other sheet** via Dashboard Actions (see Step 5)
- **Sort:** Variance Days descending (worst first)

### Sheet 8 — Significance Test Bar Chart

- **Source:** `mode_significance_tests`
- **Visual:** Horizontal bar chart with annotations
- **Rows:** `Mode`
- **Columns:** `Diff From Grand` (signed)
- **Color:** Red if positive (worse than grand mean), green if negative
- **Label:** Late rate (%) and p-value as superscript
- **Reference line:** X = 0 (grand mean)
- **Title:** "Late Rate vs Grand Mean — every mode differs significantly (p < 1e-20)"

---

## 4. Assemble the Dashboard

**File → Dashboard → New Dashboard**, size = 1440×900.

Layout:

```
+-----------------------------------------------------------------------+
| TITLE: Last-Mile Delivery Audit | DataCo Global, 2015-2018            |
+-----------------------------------------------------------------------+
| Sheet 1: 6 KPI tiles                                                  |
+-----------------------------+----------------------------------------+
| Sheet 2: OEE Scorecard      | Sheet 8: Mode Significance Bars        |
| (the hero chart)            |                                        |
|                             |                                        |
+-----------------------------+----------------------------------------+
| Sheet 3: Late Heatmap       | Sheet 5: P-Chart Small Multiples       |
| (Market × Mode)             |                                        |
|                             |                                        |
+-----------------------------+----------------------------------------+
| Sheet 4: SARIMA Forecast    | Sheet 6: Variance Box Plot             |
|                             |                                        |
+-----------------------------+----------------------------------------+
| Sheet 7: Drill-Through Detail Table                                   |
| (filtered by clicks elsewhere on the dashboard)                       |
|                                                                       |
+-----------------------------------------------------------------------+
| Filters: [Date Range] [Market] [Shipping Mode] [Customer Segment]     |
+-----------------------------------------------------------------------+
```

---

## 5. Dashboard Actions — The Drill-Through (Brief Task 4)

This is the key requirement. Open **Dashboard → Actions** and add:

### Action 1: "Drill from Heatmap to Detail" (Filter Action)

- **Type:** Filter
- **Source sheet:** Sheet 3 (Late Heatmap) AND Sheet 2 (OEE) AND Sheet 5 (P-Chart)
- **Target sheet:** Sheet 7 (Drill-Through Detail Table)
- **Run on:** Select (i.e. clicking)
- **Source fields:** `Market Name`, `Region Name`, `Shipping Mode`
- **Target field:** Same fields in the master
- **Behavior:** Clicking a cell in any of the upper charts filters the detail table to just those orders

### Action 2: "Highlight related rows" (Highlight Action)

- **Type:** Highlight
- **Source sheets:** All upper sheets
- **Target sheets:** All
- **Run on:** Hover
- **Source fields:** `Shipping Mode`
- **Behavior:** Hovering a mode highlights its data everywhere

### Action 3: "Drill to External" (URL Action — optional)

- **Type:** URL
- **Source sheet:** Sheet 7 (Drill-Through Detail)
- **Run on:** Menu (right-click)
- **URL template:** `https://your-warehouse-system.com/orders/<Order ID>`
- **Use:** Allows the executive to right-click a row and open the full source-system order

### Action 4: "Reset View" (Button)

Add a button (Dashboard → Object → Button) that navigates back to the dashboard's default view — for one-click reset after the executive finishes drilling.

---

## 6. Verification Checklist

Before publishing, verify these numbers match the notebook:

- [ ] **Sheet 1:** Total orders = **65,752**, Late rate = **54.82%**
- [ ] **Sheet 2:** Standard Class OEE = **0.5290**, First Class OEE = **0.0225**
- [ ] **Sheet 3:** Western Europe × First Class = **~96% late** (the worst single cell)
- [ ] **Sheet 4:** Forecast first-day value should be near long-run mean (~58 orders/day)
- [ ] **Sheet 5:** First Class panel shows **2 OOC weeks**; Same Day shows **5 OOC weeks**
- [ ] **Sheet 6:** Standard Class box centered near 0, First Class box centered near +1
- [ ] **Sheet 7:** Click a region in Sheet 3 → Sheet 7 should filter to just those orders (the drill-through)
- [ ] **Sheet 8:** Standard Class bar should be the only one extending LEFT (negative — better than grand mean)

---

## 7. Theme

Use a clean operations-audit palette:

| Element | Color |
|---|---|
| Title bar | Navy `#1F3864` |
| KPI good values | Green `#2E7D32` |
| KPI warning values | Amber `#E07A1F` |
| KPI critical values | Red `#C00000` |
| Chart background | White |
| Body text | Dark grey `#333333` |
| OEE excellent (>50%) | Green `#2E7D32` |
| OEE warning (20-50%) | Amber `#E07A1F` |
| OEE critical (<20%) | Red `#C00000` |
| Font | Calibri / Tableau default |

---

## 8. Publish & Export

**For Meritshot delivery:** keep as `.twbx` (packaged workbook with embedded data).

**For client demo:** publish to Tableau Public (free) at `public.tableau.com` and embed.

**For static report:** Dashboard → Export → Image → PNG (good for slide decks).

---

## Appendix — Methodology callout

Add as a text caption on the dashboard:

> **Methodology.** Source: DataCo Global supply chain dataset, 65,752 orders, 2015-01 to 2018-01, served via 4 shipping modes (Standard / First / Second / Same Day Class) across 5 markets. Time-to-delivery computed from `Days for shipping (real)` minus `Days for shipment (scheduled)`. SPC p-charts use 3σ control limits with Bonferroni correction for multi-region comparisons. SARIMA(1,1,1)x(1,1,1,7) — weekly seasonality only; monthly seasonality not detected in the data. OEE computed as Availability × Performance × Quality at the Shipping Mode level (proxy for vehicle class).
