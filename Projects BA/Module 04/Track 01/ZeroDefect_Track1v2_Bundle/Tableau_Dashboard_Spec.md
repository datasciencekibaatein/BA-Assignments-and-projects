# Tableau Dashboard Spec — Zero-Defect Operational Control

## Purpose
A self-service Operational Control dashboard for marketplace operations leadership. It surfaces the four out-of-control patterns identified in the audit (Black Friday capacity, Northern States gap, Approval queue tail, Bottom-decile sellers) and lets operators drill from headline KPIs down to specific failing orders.

**Build time estimate: 35-45 minutes** for someone comfortable with Tableau Public/Desktop.

---

## 1. Data sources

All seven CSVs live in the `outputs/` directory after running `ZeroDefect_Audit.ipynb`. Connect them as follows in Tableau:

| File | Role | Granularity | Connection |
|---|---|---|---|
| `tableau_order_master.csv` | Primary fact table | One row per delivered order (95,082) | **Primary connection** |
| `tableau_daily_kpis.csv` | SPC time series | One row per day (599 days) | Separate data source |
| `tableau_state_perf.csv` | State KPIs | One row per state (27) | Separate data source |
| `tableau_seller_perf.csv` | Seller KPIs | One row per seller (1,212) | Separate data source |
| `tableau_review_band.csv` | Margin Preservation | One row per delay band (4) | Separate data source |
| `tableau_sarima_forecast.csv` | Capacity forecast | One row per forecast day (60) | Separate data source |
| `dashboard_kpis.csv` | Headline KPI strip | One row per KPI (13) | Separate data source |

Use **Tableau Relationships** (not joins) to avoid row duplication. The master table is self-contained for most worksheets.

---

## 2. Calculated fields (all on `tableau_order_master`)

```
// 1. Lead Time Band (already in CSV but recompute for safety)
[Lead Time Band] =
IF [lead_time_days] < 5  THEN "1. <5d"
ELSEIF [lead_time_days] < 10 THEN "2. 5-10d"
ELSEIF [lead_time_days] < 15 THEN "3. 10-15d"
ELSEIF [lead_time_days] < 30 THEN "4. 15-30d"
ELSE "5. 30d+"
END

// 2. Delay Band
[Delay Band] =
IF [delivery_delay_days] <= 0 THEN "1. On-time"
ELSEIF [delivery_delay_days] <= 3 THEN "2. Late 1-3d"
ELSEIF [delivery_delay_days] <= 7 THEN "3. Late 4-7d"
ELSE "4. Late 8+d"
END

// 3. On-time flag
[Is On-Time] = IF [is_late] = 0 THEN 1 ELSE 0 END

// 4. Severely late flag (the margin-killing band)
[Is Severely Late] = IF [delivery_delay_days] > 7 THEN 1 ELSE 0 END

// 5. Pct on-time (measure)
[% On-Time] = SUM([Is On-Time]) / COUNT([order_id])

// 6. Pct severely late
[% Severely Late] = SUM([Is Severely Late]) / COUNT([order_id])

// 7. Negative review flag
[Is Negative Review] = IF [review_score] <= 2 THEN 1 ELSE 0 END

// 8. Pct negative review
[% Negative Review] = SUM([Is Negative Review]) / SUM(IF NOT ISNULL([review_score]) THEN 1 ELSE 0 END)

// 9. Region grouping (for cleaner visuals)
[Region] =
IF [customer_state] IN ("RR","AP","AM","PA","RO","AC","TO") THEN "North"
ELSEIF [customer_state] IN ("MA","PI","CE","RN","PB","PE","AL","SE","BA") THEN "Northeast"
ELSEIF [customer_state] IN ("MT","MS","GO","DF") THEN "Center-West"
ELSEIF [customer_state] IN ("MG","ES","RJ","SP") THEN "Southeast"
ELSEIF [customer_state] IN ("PR","SC","RS") THEN "South"
ELSE "Other"
END
```

---

## 3. Sheet-by-sheet build (9 worksheets → 1 dashboard)

### Sheet 1 — `KPI_Strip`
Six-up KPI tiles for the dashboard header. Use `dashboard_kpis.csv`.

- Total delivered orders: **95,082**
- Mean lead time: **12.6 days**
- On-time rate: **91.8%**
- Late by 8+ days: **3.5%** (color RED if >2%)
- Late 8+d → mean review: **1.73 / 5**
- SARIMA MAPE: **18.1%**

Build: Use Text marks. Format each as a large-number tile. Conditional formatting: red bg if metric is "bad".

### Sheet 2 — `Lead_Time_Distribution`
**Two histograms side-by-side** to make the audit's hero point visible:

Left panel: `lead_time_days` histogram (bin width = 1 day, x-axis 0-60). Annotate skew = +3.83.
Right panel: `LN(lead_time_days)` histogram (need a calculated field). Annotate skew ≈ 0.6.

**Title: "Standard SPC Fails on Raw Data — Log Transform Required"**

Drag `lead_time_days` to Columns → right-click → Create bins (size=1) → drag binned field to Columns. `Number of Records` to Rows.

### Sheet 3 — `SPC_Control_Charts`
Three stacked line charts (use Container in dashboard later):

**Panel A — Raw I-chart on daily mean lead time**
- Data source: `tableau_daily_kpis.csv`
- X-axis: `purchase_ts` (continuous date)
- Y-axis: `mean_lead`
- Reference lines (use a Reference Line per axis): UCL=18.4, LCL=−1.2, CL=11.6
- Title: **"Raw I-Chart — LCL goes negative (model misspecification)"**

**Panel B — Log-transformed I-chart**
- Same setup but Y-axis is `mean_log_lead` (use `LN(mean_lead)` if column unavailable)
- Reference lines: UCL=2.84, LCL=2.13, CL=2.49
- Title: **"Log I-Chart — Corrected SPC (interpretable LCL)"**

**Panel C — Daily p-chart on % late**
- Y-axis: `pct_late`
- Reference line (constant): mean = 0.082 (8.2%)
- Mark days where `pct_late > 0.15` in red
- Title: **"Daily Late-Rate p-chart"**

For all three: use Mark Type = Line + Circle. Set color to Navy `#1F3864` for normal points, Red `#C00000` for OOC.

### Sheet 4 — `State_Heatmap`
Brazilian state map showing mean lead time by customer state.

Build:
- New worksheet → drag `customer_state` to Detail
- Tableau should auto-recognize as Brazilian states; if not: right-click `customer_state` → Geographic Role → State/Province → set country reference to Brazil
- Mark Type: **Filled Map**
- Color: `mean_lead_days` (or AVG of `lead_time_days` from master)
  - Diverging color: Green `#2E7D32` at 8d, White at 13d, Red `#C00000` at 25d
- Tooltip: state name, n_orders, mean lead time, % late, % severely late

If filled map doesn't work in your Tableau version, fall back to a horizontal bar chart sorted by mean lead time (already shown in `figures/geographic_variance.png`).

### Sheet 5 — `Seller_Tier_Table`
Sortable table of sellers (use `tableau_seller_perf.csv`).

Columns: `seller_id` (truncate to first 8 chars), `seller_state`, `n_orders`, `mean_lead_days`, `pct_late`.

- Default sort: `pct_late` descending
- Conditional format on `pct_late`: green <8%, amber 8-15%, red >15%
- Filter: only show sellers with `n_orders >= 100` (this is the "high-volume" set of 202)
- Add a Top N filter on the dashboard: "Show worst 20 sellers"

### Sheet 6 — `Review_vs_Delay`
**The Margin Preservation hero chart** — bar chart from `tableau_review_band.csv`.

- Columns: `delay_band`
- Rows: `mean_score` (left axis) and `pct_negative_review` (right axis, dual axis)
- Mark Type: Bar (mean_score), Line + Circle (pct_negative_review)
- Color the bars: Green `#2E7D32`, Amber `#E07A1F`, Red `#C00000`, Dark Red `#7F0000` for the four delay bands
- **Annotation on Late 8+d: "1.73 / 5 stars — 76% are 1-2 stars"**
- Title: **"Lateness Collapses Reviews — The Margin Preservation Mechanism"**

### Sheet 7 — `SARIMA_Forecast`
Line chart of historical daily volume + 60-day forecast.

- Combine `tableau_daily_kpis.csv` (history) and `tableau_sarima_forecast.csv` (forecast) using Union or two separate marks on a date axis
- Historical line: Navy `#1F3864`, thin
- Forecast line: Red `#C00000`, thicker
- Confidence interval: Red shaded band using `ci_lower` and `ci_upper` (Mark Type Area)
- Annotate Black Friday 2017 spike (1,147 orders) with arrow + label
- Title: **"60-Day Capacity Forecast (SARIMA, MAPE 18.1%)"**

### Sheet 8 — `Order_Drill_Detail`
Hidden by default; appears via dashboard action. Detail table:

Columns: `order_id` (first 8 chars), `customer_state`, `seller_state`, `category_en`, `purchase_date`, `lead_time_days`, `delivery_delay_days`, `review_score`.

Filter: limited to N records (Tableau gets slow over 5K rows in tables); add a "Top 100 by delay" filter.

### Sheet 9 — `Methodology_Note`
Static text panel for the dashboard footer. Content:

> **Methodology.** SPC method: log-transformed I-MR + daily p-chart (raw I-MR fails due to skew=3.83). Hypothesis test: Kruskal-Wallis non-parametric ANOVA across 15 highest-volume states yields p < 1e-30 (geographic differences are real, not noise). Forecasting: SARIMA(1,1,1)x(1,1,1,7) with weekly seasonality and Black Friday week as exogenous regressor; holdout MAPE = 18.1%. Data trimmed before 2018-08-22 to avoid the dataset's known truncation cliff.

---

## 4. Dashboard layout (1440 × 900)

```
┌───────────────────────────────────────────────────────────────────────────┐
│  ZERO-DEFECT INITIATIVE — OPERATIONAL CONTROL DASHBOARD                  │
│  Marketplace fulfillment audit | 2017-01 to 2018-08 | 95,082 orders     │
├───────────────────────────────────────────────────────────────────────────┤
│   [KPI_Strip]   6 tiles in a row, height 80px                            │
├───────────────────────────────────────┬───────────────────────────────────┤
│                                       │                                   │
│   [Lead_Time_Distribution]            │   [SPC_Control_Charts]            │
│   width 50%, height 360px             │   width 50%, height 360px         │
│   2 histograms side-by-side           │   3 stacked panels                │
│                                       │                                   │
├───────────────────────────────────────┼───────────────────────────────────┤
│                                       │                                   │
│   [State_Heatmap]                     │   [Review_vs_Delay]               │
│   width 50%, height 280px             │   width 50%, height 280px         │
│                                       │                                   │
├───────────────────────────────────────┴───────────────────────────────────┤
│                                                                           │
│   [Seller_Tier_Table]   [SARIMA_Forecast]                                │
│   width 50%, h 280px    width 50%, h 280px                               │
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│   [Methodology_Note]   collapsible footer, height 60px                   │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Dashboard actions (the drill-through)

The brief specifies "drill-through paths to specific failure points." Set up three:

1. **State → Seller filter.** When user clicks a state on `State_Heatmap`, filter `Seller_Tier_Table` and `Order_Drill_Detail` to sellers in that state.
   - Action type: Filter
   - Source: State_Heatmap (Select)
   - Targets: Seller_Tier_Table, Order_Drill_Detail
   - Field: customer_state ↔ seller_state (or via master_table join)

2. **Seller → Order detail.** When user clicks a seller on `Seller_Tier_Table`, open the `Order_Drill_Detail` panel filtered to that seller.
   - Action type: Filter (with Select trigger)
   - Field: seller_id

3. **OOC date → Order detail.** When user clicks an out-of-control day on `SPC_Control_Charts`, filter `Order_Drill_Detail` to orders from that day.
   - Action type: Filter
   - Field: purchase_date ↔ order purchase_date

For all three, use "Run on: Select" and "Clearing the selection: Show all values".

---

## 6. Theme & formatting

| Element | Value |
|---|---|
| Primary navy | `#1F3864` |
| Operations green | `#2E7D32` |
| Warning amber | `#E07A1F` |
| Critical red | `#C00000` |
| Background | White / `#F5F5F5` |
| Title font | Calibri Bold 16pt |
| Body font | Calibri Regular 10pt |
| KPI tile font | Calibri Bold 24pt |

Use Tableau's "Format Workbook" → Fonts → set defaults globally.

---

## 7. Verification checklist

After build, validate against these locked numbers from the notebook:

| Checkpoint | Expected value |
|---|---|
| Total delivered orders | **95,082** |
| Mean lead time | **12.6 days** |
| Median lead time | **10.3 days** |
| Lead-time skewness | **+3.83** |
| On-time rate | **91.8%** |
| Late 8+ days | **3.5%** (3,336 orders) |
| Worst state — Roraima (RR) | mean lead **29.9 days**, n=40 |
| Best state — São Paulo (SP) | mean lead **8.8 days**, n=39,902 |
| Cross-state ratio | **3.4×** |
| Late 8+d → mean review | **1.73 / 5** |
| Late 8+d → % 1-2 stars | **76%** |
| On-time → mean review | **4.29 / 5** |
| Black Friday 2017 peak | **1,147 orders** on 2017-11-24 |
| SARIMA holdout MAPE | **18.1%** |
| 60-day forward forecast mean | **~231 orders/day** |

If any of these don't match, re-run the notebook from a fresh DB and re-export the CSVs.

---

## 8. Publishing

For internal sharing: publish to Tableau Server / Online with the master CSV as a Tableau Data Extract (.hyper) for performance.

For Tableau Public (free): the `tableau_order_master.csv` is 20MB which is fine. Upload as Extract.

Add the dashboard URL to the README's "Deliverables" section.
