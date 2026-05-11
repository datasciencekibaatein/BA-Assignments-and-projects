# Track 2 v4 — Pirate's Growth Strategy

**The Pirate's Growth Strategy: Scaling a Digital Ecosystem through Unit Economics**

Dataset: Online Retail II (UCI ML Repository) — 1,067,371 raw transactions, Dec 2009 → Dec 2011

---

## Workflow

1. **Open `Growth_CommandCenter.xlsx`** — 11-sheet workbook mirroring a Power BI Growth Command Center. Includes 9 KPI tiles, AARRR funnel, cohort heatmap, basket rules, segmentation, game theory matrix, decision tree, MECE roadmap, and a DAX reference sheet with 15 measures ready to lift into a `.pbix` file.
2. **Open `PirateGrowth_Audit.ipynb`** — full Python pipeline: load data → AARRR funnel → cohort retention → market basket analysis → RFM segmentation → game theory Nash → decision tree EV.
3. **Read `Project_Brief_Reframed.md`** for the rationale on why Online Retail II replaces H&M and what's different from prior versions.
4. **Read `Strategic_Recommendation.md`** for the 13-slide Pyramid deck outline (the "tell the board" version).
5. **Run `python scripts/pirate_runner.py --input data/online_retail_II.xlsx`** for a CLI version that regenerates all hero numbers.

---

## Headline findings

| Finding | Number |
|---|---|
| Total clean revenue | £17.74M |
| Customers | 5,878 |
| Mean LTV (24mo observed) | £3,019 |
| LTV/CAC ratio (gross @ 45% margin, £15 CAC) | 90.6x (see honest call-out) |
| **Activation rate (2nd purchase ≤30d)** | **23.6% — biggest funnel leak** |
| M+12 cohort retention (avg) | 18.2% |
| Top basket rule lift | 7.40x (Choc ↔ Tea Hot Water Bottles) |
| Mean lift top 5 rules | 6.52x |
| Champions segment | 1,814 customers = £13.5M LTV (76% of revenue) |
| International rev/customer | £5,709 (vs UK £2,752 = 2.07x) |
| Nash equilibrium | (Cut 15%, Cut 15%) → £16.24M / £16.24M each |
| Pareto-optimal | (Hold, Hold) → £17.50M / £17.50M each (loss to cooperation: £1.26M) |
| **EV(Dynamic Pricing)** | £47,865/yr |
| **EV(Referral Loop)** | **£719,700/yr (winner, 15x ratio)** |
| 6-month roadmap ROI | 10.6x (£105K invested → £1.108M return) |

---

## Methodology notes

### AARRR Funnel
- **Acquisition:** first-purchase event = signup proxy. 5,878 customers across 24 monthly cohorts (Dec 2009 → Nov 2011).
- **Activation:** 2nd purchase within 30 days = "they came back" milestone. Industry benchmark for e-comm gift category: 25-35%.
- **Retention:** monthly cohort survival. M+12 average across cohorts = 18.2% (industry benchmark 15-25% — within range).
- **Referral:** no native data → modeled via k-factor (Task 4).
- **Revenue:** total LTV per customer, segmented via RFM.

### Cohort Analysis
- 24 monthly cohorts × 25 months of observation.
- Best cohort (Dec 2009): 37.6% at M+12 (founder cohort effect — these are the earliest, most committed users).
- Average M+1 retention 21.2%, M+12 = 18.2% (curve flattens after M+3).

### Market Basket Analysis
- Apriori-style on top-50 products (covers ~60% of transaction volume).
- 19,347 multi-item baskets analyzed.
- Lift = P(B|A) / P(B); >2.0 = positive association; >5.0 = strong rule.
- Top 5 lift values [7.40, 7.14, 6.14, 6.12, 5.80] → mean 6.52x.
- Application: bundle these pairs at checkout, drive AOV uplift 30-40%.

### Game Theory (2-firm Nash)
- 3 strategies × 3 strategies = 9-cell payoff matrix.
- Calibration: total UK gift market £35M, demand elasticity 1.2, share shift 5pp per 7% price advantage, 45% gross margin with half-rate decay on cuts.
- Synthetic competitor (Etsy/notonthehighstreet-equivalent), clearly disclosed as not from data.
- Result: classic prisoner's dilemma — pure Nash at (Cut 15%, Cut 15%) is Pareto-dominated by (Hold, Hold).

### STP (RFM Segmentation)
- R/F/M each scored 1-4 via quartiles (R=4 means most recent).
- 6-segment rule:
  - Champions: R≥3 AND F≥3 AND M≥3
  - Loyal: R≥3 AND F≥2
  - New/Promising: R≥3 AND F≤2
  - At-Risk-VIP: R≤2 AND F≥3 AND M≥3
  - At-Risk: R≤2 AND F≥2
  - Hibernating: everything else

### Decision Tree EV
- Probabilities are subjective priors (industry benchmark anchored).
- Pricing arm: 3 scenarios × elasticity calc → ΔContribution.
- Referral arm: 3 k-factor scenarios × annualized LTV × margin + saved CAC − program cost (£50K/yr).
- Both arms annualized (24-month observation → divide by 2).

---

## Honest call-outs

1. **LTV/CAC = 90.6x is unrealistic for production.** This uses observed historical data with a £15 CAC benchmark. Real-world e-commerce CAC at scale (paid social + search) lands at £30-50. At £30 CAC, ratio = 45x; at £50 CAC, 27x — both still very healthy and well above the 3.0x threshold. The brief's "high CAC" framing is about *future scaling* CAC, not what the data shows.

2. **22.8% of rows have null Customer_ID** — these are anonymous walk-ins, dropped from cohort and segmentation analysis. The 5,878 customer count refers to identified customers only. This is consistent with how Online Retail II is typically analyzed in literature.

3. **No referral chain in the data.** k-factor scenarios (0.10, 0.20, 0.30) are industry benchmarks, not observed. Real virality at e-comm gift category is closer to k=0.05-0.15; we used 0.10-0.30 to span the full plausible range and still won by 15x.

4. **No competitor data.** Game Theory uses a calibrated synthetic competitor (Etsy/notonthehighstreet-equivalent at £35M total market). Clearly labeled in the workbook and deck.

5. **2009-2011 era data.** Numbers are real but 14 years old. UK gift retail e-commerce has matured significantly since (Brexit, Amazon expansion, etc.). The methodology transfers; the absolute numbers should be re-baselined on current data before board approval.

6. **24-month observation window.** LTV is observed over 24 months, not predicted. Longer windows (5-year typical for SaaS LTV) would yield higher LTV. We annualized by dividing by 2.

7. **Decision tree probabilities are priors, not data.** P(Aggressive)=0.30, P(Moderate)=0.50, P(Conservative)=0.20 reflect a "central scenario most likely" prior. Sensitivity: even if you flip these (P=0.5 aggressive, 0.3 moderate, 0.2 conservative), Pricing EV moves to ~£40K — still loses to Referral by ~18x.

8. **The "biggest funnel leak" call.** Activation drop-off (76.4%) and M0→M1 retention drop-off (78.8%) are mathematically close. We call Activation the bigger leak because (a) it's the upstream gate, (b) any retention investment is wasted on customers who never activated. Both are addressed in the MECE roadmap.

---

## Continuity vs prior tracks (Track 2 portfolio)

This is the fourth orthogonal lens in the Track 2 family. The intentional differentiation:

| Lens | v1 IBM HR | v2 Google Play | v3 IBM Telco | **v4 Online Retail II** |
|---|---|---|---|---|
| Hero method | Logistic regression | Elasticity + premium pivot | Churn + EV decisioning | **AARRR + LTV/CAC + Nash + EV** |
| Hero metric | Attrition 16.12% | Elasticity −0.106 | Churn 26.5%, AUC 0.844 | **Activation 23.6%, M+12 18.2%** |
| Hero $ | $1.4M attrition cost | $204.6M GMV | $970K 12-mo | **£17.7M rev, EV(Ref) £720K** |
| Strategic frame | Workforce risk | Pricing pivot | Product pivot | **Growth strategy** |
| Statistical hero | Odds ratios | Price elasticity | AUC, EV per customer | **Cohort survival, MBA lift, Nash** |

A reviewer reading all four should see: same broad portfolio space (consumer/subscription analytics), four genuinely different analytical philosophies.

---

## Files

```
PirateGrowth_Track2v4_Bundle/
├── PirateGrowth_Audit.ipynb           # 22 cells, executes clean
├── Growth_CommandCenter.xlsx          # 11 sheets, 58 formulas, 26 defined names, 15 DAX measures
├── Project_Brief_Reframed.md          # rationale + diff vs original H&M brief
├── Strategic_Recommendation.md        # 13-slide deck outline
├── README.md                          # this file
├── data/
│   └── online_retail_II.xlsx          # source data (UCI ML Repository)
└── scripts/
    └── pirate_runner.py               # CLI for AARRR + cohort + MBA + RFM + Nash + EV
```
