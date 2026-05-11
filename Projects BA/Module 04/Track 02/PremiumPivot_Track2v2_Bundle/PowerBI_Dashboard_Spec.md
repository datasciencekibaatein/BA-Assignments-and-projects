# Power BI - "Growth Command Center" Dashboard Spec

> Marketing & Product growth dashboard for the Premium Pivot recommendation.
> 9 visuals across 4 sheets. Theme: navy (#1F3864) / green (#2E7D32) / red (#C00000) / amber (#E07A1F).
> Resolution: 1440 x 900.

---

## 1. Data Sources (load order)

Connect Power BI Desktop to the 7 CSVs in `outputs/` plus the SQLite database for richer joins.

| Source | File | Rows | Role |
|---|---|---|---|
| Apps Master | `powerbi_app_master.csv` | 9,638 | Fact table (one row per app, all dimensions joined) |
| Segments | `powerbi_segments.csv` | 9,638 | Joins to Apps via app_id - segment label per app |
| Elasticity | `powerbi_elasticity.csv` | 7 | Per-category elasticity + recommended pricing strategy |
| Funnel | `powerbi_funnel.csv` | 9,638 | Per-app funnel rates (install -> review -> advocate) |
| Bullwhip | `powerbi_bullwhip.csv` | 33 | Per-category CV ratio + amplification factor |
| DuPont | `powerbi_dupont.csv` | 18 | Per-category 3-component decomposition |
| Recommendations | `powerbi_recommendations.csv` | 7 | Per-category projected GMV lift |
| KPIs | `dashboard_kpis.csv` | 14 | Headline metrics for the top strip |

Optionally connect to `outputs/playstore.db` (SQLite) for direct view access.

### Table relationships

```
apps_master (fact)
  |--- segments        on app_id    (1:1)
  |--- funnel          on app_id    (1:1)
  |--- elasticity      on category  (many:1)
  |--- bullwhip        on category  (many:1)
  |--- dupont          on category  (many:1)
  |--- recommendations on category  (many:1)
```

---

## 2. DAX Calculated Measures

Create these in a dedicated `_Measures` table (best practice):

### Marketplace KPIs
```DAX
Total Apps              = COUNTROWS(apps_master)
Paid Apps               = CALCULATE(COUNTROWS(apps_master), apps_master[is_paid] = 1)
% Paid                  = DIVIDE([Paid Apps], [Total Apps])
Total Installs (B)      = SUM(apps_master[n_installs]) / 1000000000
Total GMV ($M)          = SUMX(apps_master, apps_master[price_usd] * apps_master[n_installs]) / 1000000
Yield Per Install ($)   = DIVIDE(SUMX(apps_master, apps_master[price_usd] * apps_master[n_installs]), SUM(apps_master[n_installs]))
Avg Paid Price ($)      = AVERAGEX(FILTER(apps_master, apps_master[is_paid] = 1), apps_master[price_usd])
```

### Funnel
```DAX
Cohort Installs (B)     = CALCULATE(SUM(apps_master[n_installs]), funnel[pct_positive] <> BLANK()) / 1000000000
Cohort Reviewers (B)    = CALCULATE(SUM(apps_master[n_reviews]), funnel[pct_positive] <> BLANK()) / 1000000000
Install -> Review %     = DIVIDE([Cohort Reviewers (B)], [Cohort Installs (B)])
Cohort Advocates (B)    = SUMX(funnel, funnel[advocate_count]) / 1000000000
Install -> Advocate %   = DIVIDE([Cohort Advocates (B)], [Cohort Installs (B)])
```

### Elasticity & Pivot
```DAX
Naive Elasticity        = 0.302   /* hardcoded - the "wrong answer" reference */
Corrected Elasticity    = -0.106  /* hardcoded - the hero finding */
Sign Flip               = [Corrected Elasticity] - [Naive Elasticity]    /* = -0.408 */

Active Scenario         = SELECTEDVALUE('Scenario Picker'[Scenario], "Smart Skim")
Active Price Change     = SWITCH([Active Scenario],
                                 "Status Quo", 0,
                                 "Universal +20%", 0.20,
                                 "Smart Skim", 0.30,
                                 "Subscription Pivot", 0.10, 0)
Active Volume Effect    = [Corrected Elasticity] * [Active Price Change]
Projected GMV ($M)      = [Total GMV ($M)] * (1 + [Active Price Change]) * (1 + [Active Volume Effect])
GMV Lift ($M)           = [Projected GMV ($M)] - [Total GMV ($M)]
GMV Lift %              = DIVIDE([GMV Lift ($M)], [Total GMV ($M)])
```

### DuPont decomposition
```DAX
Volume Component        = SUM(dupont[comp1_total_installs]) / 1000000
Conversion Component    = AVERAGE(dupont[comp2_paid_install_rate])
Price Component         = AVERAGE(dupont[comp3_avg_paid_price])
Identity Check ($M)     = SUMX(dupont, dupont[comp1_total_installs] * dupont[comp2_paid_install_rate] * dupont[comp3_avg_paid_price]) / 1000000
```

### Bullwhip
```DAX
Avg Amplification       = AVERAGE(bullwhip[amplification])
High Amp Categories     = CALCULATE(COUNTROWS(bullwhip), bullwhip[amplification] > 1.2)
```

### 7Ps Marketing Mix tracking
```DAX
P1 Product Categories   = DISTINCTCOUNT(apps_master[category])           /* 33 */
P2 Price Median ($)     = MEDIANX(FILTER(apps_master, apps_master[is_paid]=1), apps_master[price_usd])
P3 Place Coverage       = "Google Play (single channel)"                  /* placeholder */
P4 Promotion (CAC reduction)  = [Active CAC Reduction] /* from scenario */
P5 People (developer count, proxy)   = DISTINCTCOUNT(apps_master[category])  /* proxy: distinct categories ~ active dev community */
P6 Process Funnel Stages = 4   /* Install -> Reviewer -> Advocate -> Detractor */
P7 Physical Evidence Avg Rating = AVERAGE(apps_master[rating])
```

---

## 3. Sheet 1 - "Pivot Cockpit" (executive summary)

**Layout (1440 x 900):**

```
+--------------------------------------------------------------+
| HEADER STRIP - 6 KPI TILES (height ~120)                     |
| 9,638 apps  |  $204.6M GMV  |  $0.003/install  |             |
| -0.106 elas |  +21.9% lift  |  +$38M GMV impact              |
+--------------------------------------------------------------+
|                                                              |
|  LEFT: Scenario Comparison Bar (waterfall)         RIGHT:    |
|                                                    Active    |
|  Status Quo  $204.6M  --                          Scenario   |
|  Universal   $240.3M  +$36M (+17.5%)              picker     |
|  Smart Skim  $257.5M  +$53M (+25.9%) <-- Hero     (slicer)   |
|  Sub Pivot   $228.0M  +$23M (+11.4%)              + KPI      |
|                                                    delta     |
|                                                    cards     |
|                                                              |
+--------------------------------------------------------------+
|                                                              |
|  BOTTOM: Pyramid recommendation block (text + 3 supporting)  |
|                                                              |
+--------------------------------------------------------------+
```

**Visuals on this sheet:**

1. **KPI Strip** - 6 card visuals across the top:
   - Total Apps (9,638)
   - Total Paid GMV ($204.6M)
   - Yield/Install ($0.003)
   - Corrected Elasticity (-0.106) with subtitle "Naive: +0.30 wrong sign"
   - Active Scenario lift % (color: green if positive, red if negative)
   - Active Scenario lift $ ($M)

2. **Waterfall Chart** - Status Quo -> Smart Skim
   - Bars: baseline GMV, +price effect, +volume effect, = projected GMV
   - X-axis: cumulative bars; Y-axis: GMV ($M)
   - Highlight Smart Skim total in amber

3. **Scenario Slicer** - tile slicer with 4 buttons (Status Quo, Universal +20%, Smart Skim, Subscription Pivot)
   - Default: Smart Skim selected
   - Slicer drives `Active Scenario` measure

4. **Recommendation Block** - text card with the Pyramid Principle answer:
   - Top: "Adopt Smart Skim - lift inelastic-category prices 30%, drop elastic 10%, smooth marketing in bullwhip categories. Projected lift: +21.9% (~$38M)."
   - 3 supporting bullets (one each for elasticity, segmentation, DuPont)

---

## 4. Sheet 2 - "Elasticity & Pricing Strategy"

**Layout:**

```
+--------------------------------------------------------------+
| TOP-LEFT: Naive vs Corrected comparison    TOP-RIGHT:        |
| Two huge number cards side by side          Quality control  |
|                                              regression      |
| NAIVE = +0.302  (red)                        equation        |
| CORRECTED = -0.106 (green, amber bg)         + R squared,    |
|                                              p-value         |
+--------------------------------------------------------------+
|                                                              |
|  CENTRE: By-category elasticity bar chart                    |
|  - X-axis: elasticity value (centred at 0)                  |
|  - Y-axis: 7 categories sorted by elasticity                |
|  - Bar color: red if elastic (e<-0.3), green if inelastic    |
|  - Label: each bar shows recommended action                  |
|                                                              |
+--------------------------------------------------------------+
|                                                              |
|  BOTTOM: Strategy table - per-category recommendation        |
|  Category | Elasticity | p-value | Action | Δ Price | Δ Q   |
|                                                              |
+--------------------------------------------------------------+
```

**Visuals:**

5. **Elasticity Comparison** - two number cards (NAIVE vs CORRECTED) with color coding and a tooltip showing the regression formula
6. **By-Category Elasticity Bar** - horizontal bar chart from `elasticity` table; conditional color (red <-0.3, amber 0 to -0.3, green >0)
7. **Strategy Table** - matrix from `recommendations` table

---

## 5. Sheet 3 - "Funnel & Bullwhip"

**Layout:**

```
+--------------------------------------------------------------+
| TOP-LEFT: Funnel chart (4 stages)                            |
| Install   21.79B                                             |
| Reviewer   0.58B (2.66%)                                     |
| Advocate   0.34B (1.57%)                                     |
| Detractor  0.18B (0.84%)                                     |
+--------------------------------------------------------------+
|                                                              |
|  TOP-RIGHT: Per-app medians                                 |
|  3 cards: Median review rate, advocate rate, % positive     |
|                                                              |
+--------------------------------------------------------------+
|                                                              |
|  BOTTOM: Bullwhip ranking (15 categories)                   |
|  Horizontal bars sorted by amplification                    |
|  Red if >1.2 (high), amber 0.9-1.2, green <0.9              |
|                                                              |
+--------------------------------------------------------------+
```

**Visuals:**

8. **Funnel Visualization** - native Power BI Funnel chart (4 stages, stage drop-off labels)
9. **Bullwhip Bar Chart** - from `bullwhip` table, sorted descending by amplification

---

## 6. Sheet 4 - "DuPont Decomposition"

**Layout:**

```
+--------------------------------------------------------------+
|  TOP: Identity equation card                                 |
|  Paid GMV = Total Installs x Paid Conversion x Avg Price     |
|  Identity check ($M): [Identity Check ($M)] vs Total GMV     |
+--------------------------------------------------------------+
|                                                              |
|  CENTRE: Bubble chart (the hero visual)                      |
|  - X axis: log10(Total Installs)                            |
|  - Y axis: Paid Conversion Rate (%)                          |
|  - Bubble size: Paid GMV                                     |
|  - Bubble color: Avg Price (gradient navy -> orange)         |
|  - Tooltip: full DuPont decomposition for that category      |
|                                                              |
+--------------------------------------------------------------+
|                                                              |
|  BOTTOM: Decomposition table for top 15 categories           |
|                                                              |
+--------------------------------------------------------------+
```

**Visuals:**

(Bubble chart and decomposition table - reuses visual #4 from the notebook)

---

## 7. Dashboard Actions / Drill-Through

- **Click a category bar (any chart)** -> filters all visuals on the page to that category
- **Click a segment in the Pivot Cockpit** -> navigates to a category-specific drill page showing the 3-4 apps that drive that segment
- **Hover any KPI** -> tooltip shows the underlying calculation and source

---

## 8. 7Ps Marketing Mix Tracking

The Pyramid deck mentions 7Ps. Surface them as a small auxiliary tile group on Sheet 1:

| P | Metric | Current Value |
|---|---|---|
| Product | # Categories | 33 |
| Price | Median paid price | $2.99 |
| Place | Distribution channel | Google Play (single) |
| Promotion | CAC reduction lever | 10% (active when Smart Skim selected) |
| People | Active developer ecosystem (proxy) | 33 categories with paid apps |
| Process | Funnel stages tracked | 4 (Install -> Review -> Advocate -> Detractor) |
| Physical Evidence | Avg app rating | 4.17 |

---

## 9. Verification Checklist - exact numbers Power BI must produce

After building, verify each visual against the locked baseline:

| Metric | Expected Value | Where |
|---|---|---|
| Total apps | 9,638 | KPI strip |
| Paid apps | 734 | KPI strip |
| % Paid | 7.6% | KPI strip |
| Total installs | 75.3 B | KPI strip |
| Total paid GMV | $204.6 M | KPI strip |
| Yield per install | $0.003 | KPI strip |
| Naive elasticity | +0.302 | Sheet 2 |
| Corrected elasticity | -0.106 | Sheet 2 |
| R-squared | 0.898 | Sheet 2 |
| p-value | 0.045 | Sheet 2 |
| Install -> Reviewer | 2.66% | Sheet 3 |
| Install -> Advocate | 1.57% | Sheet 3 |
| Top bullwhip category | SOCIAL (3.37) | Sheet 3 |
| FAMILY paid GMV | $105.7 M | Sheet 4 |
| MEDICAL avg price | $10.62 | Sheet 4 |
| MEDICAL paid conversion | 1.46% | Sheet 4 |
| Smart Skim total revenue | $257.5 M | Sheet 1 (when Smart Skim selected) |
| Smart Skim lift % | +25.9% | Sheet 1 |
| Smart Skim lift $ | +$52.9 M | Sheet 1 |

---

## 10. Theme & Styling

```
Primary navy:    #1F3864 (headers, KPI bars)
Success green:   #2E7D32 (positive metrics, "skim/inelastic" labels)
Alert red:       #C00000 (negative metrics, "elastic/penetrate" labels)
Amber accent:    #E07A1F (highlight winning scenario, hero numbers)
Light grey:      #F5F5F5 (backgrounds)
Yellow warn:     #FFFF00 (critical assumption inputs)

Font: Segoe UI (Power BI native)
KPI cards: large numerals (32-40pt), small subtitle (10pt)
```

---

## 11. Methodology Note (footer)

Add a small footer text block on Sheet 1:

> **Methodology**: Cross-sectional log-log price regression with category fixed effects, app rating, and log(reviews) controls (n=587 paid apps with rating data). Quality-controlled elasticity = -0.106 (p=0.045, R squared=0.898). DuPont-style decomposition follows the standard multiplicative-decomposition discipline applied to marketplace unit economics. Funnel uses sentiment-tagged reviews as Advocate/Detractor proxies. All projections assume small-change linearity around the current price point - large jumps require structural re-estimation. GMV is a price x install volume proxy, not literal revenue (only some installs convert to purchase).
