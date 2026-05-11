# The Premium Pivot - Track 2 (Product & Consulting)

> Strategic re-positioning of a marketplace subscription ecosystem.
> Anchor: **Google Play Store** (9,638 apps, 75.3B installs, 33 categories).
> Hero finding: naive elasticity = +0.30 (wrong sign); quality-controlled = -0.11 (highly inelastic).
> Recommendation: **Smart Skim pivot** lifts GMV by +25.9% (~$53M) without significant install volume loss.

---

## 1. Files in this bundle

| File | Purpose |
|---|---|
| `PremiumPivot_Audit.ipynb` | End-to-end analytics notebook (Python, 8 parts) |
| `PremiumPivot_Engine.xlsx` | 10-sheet financial model with 4 pivot scenarios + active scenario picker |
| `PowerBI_Dashboard_Spec.md` | "Growth Command Center" - 9 visuals across 4 sheets, with DAX measures |
| `Pyramid_Deck_Outline.md` | McKinsey-style 11-slide deck (SCR + Pyramid Principle structure) |
| `sql/schema.sql` | SQLite schema - 4 tables + 5 analytical views |
| `sql/load_data.py` | Python loader: cleans CSVs, builds the SQLite DB |
| `README.md` | This file |

---

## 2. Folder layout for running

Place the bundle into the following folder structure (the notebook's path setup auto-resolves either way - by folder name or by sibling directories):

```
Module 03/
└── Track 02/
    └── premium_pivot/
        ├── PremiumPivot_Audit.ipynb
        ├── PremiumPivot_Engine.xlsx
        ├── PowerBI_Dashboard_Spec.md
        ├── Pyramid_Deck_Outline.md
        ├── README.md
        ├── sql/
        │   ├── schema.sql
        │   └── load_data.py
        ├── data/                  <-- Drop the 2 Kaggle CSVs here
        │   ├── googleplaystore.csv
        │   └── googleplaystore_user_reviews.csv
        ├── outputs/               <-- Created by the loader/notebook
        └── figures/               <-- Created by the notebook
```

**Datasets needed** (from Kaggle - "Google Play Store Apps" by Lavanya Gupta):
- `googleplaystore.csv` (~1.3 MB, 10,841 rows)
- `googleplaystore_user_reviews.csv` (~7.4 MB, 64,295 rows)

---

## 3. Workflow

### Step 1 - Build the database
```bash
cd "Module 03/Track 02/premium_pivot"
python sql/load_data.py
```
Output: `outputs/playstore.db` (~4.6 MB SQLite database with 4 tables + 5 views).

### Step 2 - Run the notebook
Open `PremiumPivot_Audit.ipynb` in Jupyter or VS Code. Run all cells. The notebook:
- auto-resolves paths (no need to edit anything)
- regenerates the SQLite DB if missing
- produces 8 CSVs in `outputs/` for Power BI
- produces 6 PNGs in `figures/`

Total runtime: ~30 seconds.

### Step 3 - Open the Excel engine
`PremiumPivot_Engine.xlsx` ships with the analysis pre-loaded. Toggle the Active Scenario in cell `C12` of the **Pivot_Scenarios** sheet to switch between:
1. Status Quo
2. Universal +20% (naive uplift)
3. **Smart Skim** (recommended)
4. Subscription Pivot

The **Summary** sheet shows total revenue, lift $, and lift % updating live.

### Step 4 - Build Power BI dashboard
Follow `PowerBI_Dashboard_Spec.md`. Connect to the 7 CSVs in `outputs/` (or the SQLite DB directly), build the DAX measures listed in the spec, then construct the 4 sheets (Pivot Cockpit, Elasticity & Pricing, Funnel & Bullwhip, DuPont Decomposition).

### Step 5 - Build the deck
Use `Pyramid_Deck_Outline.md` as the slide-by-slide source. Each slide has a headline, body content, and visual specification. Pull figures from `figures/` directly into PowerPoint/Google Slides.

---

## 4. Headline findings

| Metric | Value | Significance |
|---|---|---|
| Total apps in scope | 9,638 | After dedup, price < $100 filter |
| Paid apps | 734 (7.6%) | Small premium tier - the underpriced segment |
| Total marketplace installs | 75.3 B | The volume is there |
| Total paid GMV | $204.6 M | Yield: $0.003/install (strategic monetization failure) |
| **Naive elasticity** | **+0.302** | Wrong sign - quality confounding |
| **Quality-controlled elasticity** | **-0.106** | p=0.045, R squared=0.898 - the hero finding |
| Install -> Reviewer | 2.66% | First-stage funnel leak |
| Install -> Advocate | 1.57% | After positive sentiment filter |
| Top bullwhip category | SOCIAL (CV ratio = 3.37) | Marketing variance > install variance |
| **Smart Skim total revenue** | **$257.5 M** | +25.9% lift over baseline |
| **Smart Skim lift in dollars** | **+$52.9 M** | ~50% improvement over naive uplift |
| Subscription Pivot revenue | $228 M | +11.4% (sidecar play) |

---

## 5. Methodology notes

### MECE Decomposition
Total Marketplace Revenue change is decomposed into 3 mutually-exclusive, collectively-exhaustive branches:
- **PRICE** (avg price changes)
- **VOLUME** (paid install count changes)  
- **MIX** (category composition shifts)

This is the top of the issue tree; sub-issues are surfaced in `MECE_Tree` sheet.

### STP Segmentation
K-means clustering with k=4 on three features:
- log10(installs) - scale dimension
- log10(price + 1) - monetization dimension
- rating - quality dimension

Features standardized before clustering. Segments are labeled by post-hoc profiling: Mass-Free, Premium-Paid, Mass-Quality, Underperforming.

### Price Elasticity (the hero method)

**Naive (wrong) approach:**
```
ln(installs) = α + β × ln(price) + ε
```
Yields β = +0.30. Positive sign because higher-priced apps tend to be higher-quality.

**Quality-controlled (correct) approach:**
```
ln(installs) = α + β × ln(price) + γ × rating + δ × ln(reviews) + Σ category_FE + ε
```
Yields β = -0.106 (p=0.045, R squared=0.898). Now we are estimating the price effect *after* controlling for the confounding quality signals.

**By-category elasticity** is estimated separately for each category with n>=20 paid apps, using the same controls (rating + log_reviews) but no category FE within the subset.

### Marketplace Unit-Economics Decomposition (DuPont analog)

The brief asks for a DuPont analysis. We don't have corporate financials, so we apply the same multiplicative-decomposition discipline to marketplace economics:

```
Paid GMV = Total Installs × Paid Conversion Rate × Avg Paid Price
         (≈ Asset Turnover)  (≈ Net Margin)        (≈ Equity Multiplier)
```

This decomposition holds as an exact identity at the category level (verified on the top 3 categories in the notebook). The advantage over corporate DuPont: we have 18 "mini-companies" (categories with 5+ paid apps) to compare, which lets us identify the dominant lever for each.

### Funnel Analysis
4-stage funnel: Install -> Reviewer -> Advocate -> Detractor, where Advocate/Detractor proxies are the count of positive/negative sentiment-tagged reviews per app. Cohort restricted to 816 apps with both install data and sentiment-tagged reviews.

### Bullwhip Diagnostic
For each category with n>=10 apps:
```
Amplification = CV(reviews_per_app) / CV(installs_per_app)
```
> 1 means review-volume variance exceeds install-volume variance, indicating that a small change in user attention triggers a disproportionately large swing in review volume - which marketing teams typically over-respond to with spend reallocation.

---

## 6. Marketplace yield model

**Current state:** $204.6M GMV / 75.3B installs = $0.003 per install.

**Post Smart Skim:** $257.5M / ~73B installs (after small volume drop in inelastic categories) = $0.0035 per install.

A 17% improvement in yield-per-install with marginal volume loss - achievable because the marketplace's true demand curve is much steeper than the surface-level evidence suggests.

---

## 7. The 4 scenarios (with Active Scenario picker in Excel)

| Scenario | Price Δ | Volume Δ | CAC Δ | Sub Lift | Total Rev | Lift $ | Lift % |
|---|---|---|---|---|---|---|---|
| 1. Status Quo | 0% | 0% | 0% | 0% | $204.6M | $0M | 0% |
| 2. Universal +20% | +20% | -2.1% | 0% | 0% | $240.3M | +$35.7M | +17.5% |
| 3. **Smart Skim** | +30% | -3.2% | -10% | 0% | **$257.5M** | **+$52.9M** | **+25.9%** |
| 4. Subscription Pivot | +10% | -1.1% | -10% | 0.5% on 57M base | $228.0M | +$23.4M | +11.4% |

**Lead recommendation: Smart Skim.** Subscription is a longer-rollout sidecar with infrastructure dependencies; Smart Skim is implementable in ~90 days.

---

## 8. Honest call-outs (don't skip these)

1. **GMV is a proxy, not literal revenue.** GMV = price × install count assumes 100% conversion of installs to paid. Actual paid conversion is unobserved. The numbers are directional but should be validated against Play Store revenue API post-launch.

2. **Cross-sectional elasticity ≠ within-app elasticity.** The -0.11 estimate is *between* apps in the steady state. A single app raising its price could see different behavior. Recommendation: A/B holdout in Phase 1 of Smart Skim rollout.

3. **Funnel uses sentiment-tagged reviews as Advocate/Detractor proxies.** Real "advocacy" (referrals, organic shares) is not in the dataset. Sentiment polarity is a reasonable approximation but not ground truth.

4. **Subscription model assumes 0.5% conversion lift on the paid-app install base (57M).** This is an industry-typical figure for subscription tier launches. Pilot in MEDICAL category first (highest WTP) to calibrate before full rollout.

5. **Bullwhip diagnostic is heuristic.** True marketing-spend bullwhip would require ad-spend time series data we don't have. The CV-of-reviews / CV-of-installs ratio is a reasonable proxy but not definitive.

6. **Categories with <20 paid apps were excluded from per-category elasticity** (statistical reliability). This means some categories (BOOKS, NEWS, etc.) don't get specific elasticity recommendations.

7. **The Subscription Pivot scenario should be read as a planning estimate, not a forecast.** The infrastructure to support a paid subscription tier doesn't exist today; the 18-month rollout assumption requires buy-in from billing/auth teams.

---

## 9. What's deliberately left out

- **Time-series elasticity.** The dataset is a single snapshot; we cannot estimate how elasticity has changed over time. A future audit could use Play Store historical data scraped over months.
- **Competitive dynamics.** We only see Play Store data; what Apple App Store, Steam, or DTC subscription competitors do is not modeled. The recommendations are about Play Store's internal tiering, not market-share war games.
- **Cohort analysis.** Per-developer analysis (e.g., "do publishers with multiple apps price differently?") is left for future work.
- **Causal inference.** OLS with controls is correlation-aware, not causal. A clean causal estimate would require natural experiments (e.g., a Play Store-wide pricing policy change).

---

## 10. Verification numbers (for QA)

After running the notebook end-to-end, the following should appear in `outputs/dashboard_kpis.csv`:

| metric | value |
|---|---|
| Total apps | 9638 |
| Paid apps | 734 |
| % paid | 7.6% |
| Total installs (B) | 75.32 |
| Total paid GMV ($M) | 204.6 |
| Yield per install ($) | 0.0027 |
| Naive elasticity | 0.302 |
| Quality-controlled elasticity | -0.106 |
| Elasticity p-value | 0.0454 |
| Elasticity R squared | 0.898 |
| Funnel: Install -> Review | 2.664% |
| Funnel: Install -> Advocate | 1.566% |
| Premium Pivot total GMV lift ($M) | 38.0 |
| Premium Pivot total GMV lift (%) | +21.9% |

Note: The Excel `Summary` sheet reports the **revenue** lift including the CAC reduction lever (+$52.9M for Smart Skim), while the notebook's per-category projection table reports the pure GMV lift ($+38M for the price-only Smart Skim). Both are correct; they measure different aggregates.
