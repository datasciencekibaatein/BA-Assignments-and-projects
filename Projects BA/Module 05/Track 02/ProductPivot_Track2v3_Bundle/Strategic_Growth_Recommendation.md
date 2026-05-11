# Strategic Growth Recommendation — Pyramid Deck Outline

**Engagement:** PivotCo "Product Pivot" — SaaS Lifecycle Optimization Track 2 v3
**Audience:** Product Manager + CPO + VP Customer Success
**Format:** ~12 slides, McKinsey Pyramid Principle structure

---

## Opening Frame (SCR — Situation, Complication, Resolution question)

**Situation.** PivotCo runs a B2B subscription-services business: phone, internet, security, backup, device protection, tech support, and streaming bundled into recurring subscriptions. ~$200M ARR, ~7,043 active subscribers, predominantly month-to-month contracts. Standard SaaS retention metrics; no formal churn-prediction discipline.

**Complication.** Annual churn is **26.5%**. Month-to-month subscribers (55% of the book) churn at **42.7%** — their expected lifetime is just **2.3 months**. Two-year subscribers churn at **2.8%** with **35.3-month lifetime**. The Product Manager is being asked to choose between **Feature Enhancement** (deeper engagement) and **Market Expansion** (new acquisitions) — but neither addresses the actual leak: **PivotCo is acquiring customers faster than it can keep them past month 6**.

**Question.** Where should the next $1M of product investment go to maximize 12-month LTV?

---

## Slide 1 — Title + Executive Summary

**Title:** *PivotCo's Real Problem Isn't Acquisition — It's That Customers Don't Stick. Skimming Beats Penetration by 4×.*

**Subtitle:** *SaaS lifecycle optimization with 7,043 customers, AUC=0.844 churn model*

**Hero box (single sentence):**
> **Skimming wins on every realistic parameter combination.** Per-customer EV: Skimming = +$198 / Penetration = −$34. Targeting just the At-Risk High Spenders segment unlocks $4.5M LTV upside in year 1.

**Three supporting tiles:**
- **FUNNEL:** First 6 months absorb 53% of all churn — onboarding is the leak
- **SEGMENT:** At-Risk High Spenders (1,465 customers, $93/mo, 52% churn) = top priority
- **STRATEGY:** Skimming via 2-year contract migration, not month-to-month volume

---

## Slide 2 — Pyramid: The Argument in One Picture

```
            TOP: Pivot to Skimming + save At-Risk High Spenders
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
   EV MATH                    SEGMENT TARGETING       PROCESS LEVER
   Skimming +$198/cust        At-Risk HS = $71K/mo    1-feature trap
   Penetration -$34/cust      = $4.5M LTV exposure    closes via 30/60/90
   Sensitivity robust                                  onboarding redesign
```

---

## Slide 3 — TASK 1: User Behavior — The Activation Cliff

**Headline:** *Half of PivotCo's customers churn before month 6.*

**Visual:** 5-stage funnel (horizontal stacked bars: retained vs churned per tenure bucket)

**Key data points:**
- Awareness (0–6mo): **52.9% churn** — the cliff
- Activation (7–12mo): 35.9% churn
- Engagement (13–24mo): 28.7% churn
- Retention (25–48mo): 20.4% churn
- Advocacy (49–72mo): **9.5% churn** — sticky once they stay

**Speaker notes:** 53% of all churners are in their first 6 months. Onboarding is broken. No marketing campaign fixes this; it requires product process redesign.

---

## Slide 4 — TASK 2a: MECE Root-Cause Decomposition

**Headline:** *Five orthogonal axes — three are about commitment, two are about engagement.*

**Visual:** 5-panel chart, one per branch:
1. Contract Friction (39.9pp spread): MTM 42.7% → 2-yr 2.8%
2. Service Quality (34.5pp): Fiber optic 41.9% → No internet 7.4%
3. Payment Friction (30.1pp): E-check 45.3% → Credit auto 15.2%
4. Feature Engagement (40.5pp): 1 feature 45.8% → 6 features 5.3%
5. Demographic Risk (51.9pp): Senior+MTM 54.6% → Non-sr+2yr 2.7%

**Speaker notes:** All 5 branches show real signal. Contract Friction is the most actionable lever (we control contract design); Service Quality (Fiber optic anomaly) is the most diagnostic (suggests an SLA mismatch worth investigating).

---

## Slide 5 — TASK 2b: STP Segmentation

**Headline:** *Four actionable segments. Save campaign starts with At-Risk High Spenders.*

**Visual:** Segment bubble chart (x=monthly $, y=tenure, size=count, color=churn rate)

| Segment | n | Churn | Monthly | LTV | Action |
|---|---|---|---|---|---|
| High Value Loyalists | 1,419 | 11% | $94.52 | $4,631 | Defend |
| **At-Risk High Spenders** | **1,465** | **52%** | **$92.90** | **$1,719** | **Save campaign first** |
| Low Engagement Newcomers | 1,366 | 44% | $47.50 | $195 | Onboarding intervention |
| Sticky Basics | 471 | 2% | $28.80 | $1,843 | Maintain |
| Mainstream | 2,322 | 15% | $60.90 | $1,955 | Standard care |

**Speaker notes:** At-Risk High Spenders has the worst combination — high spend + month-to-month + half-churn. $71K monthly revenue at risk just from this segment.

---

## Slide 6 — TASK 3: The Decision Tree

**Headline:** *Skimming dominates Penetration by 4× per customer.*

**Visual:** Decision tree diagram with two branches; EV computed at each leaf

```
            PRODUCT ROADMAP DECISION
                  |
        ┌─────────┴─────────┐
        ▼                   ▼
   SKIMMING            PENETRATION
   (2yr migration)     (MTM acquisition)
        │                   │
   p=20% convert       p=30% acquire
   gain = $1,990       gain = $155
   cost = $200         cost = $80
        │                   │
   EV = +$198          EV = -$34

   RECOMMENDATION: SKIMMING (4× advantage)
```

**Speaker notes:** Penetration is *negative EV* at base case. Even if we drop the cost to $50 and bump conversion to 40%, Penetration EV = $12. Skimming wins easily.

---

## Slide 7 — Sensitivity: Robustness of the Recommendation

**Headline:** *Skimming wins across the entire realistic parameter range.*

**Visual:** 2D heatmap (conversion rate × investment cost) with EV values

| Conv \\ Cost | $100 | $200 | $300 | $400 | $500 |
|---|---|---|---|---|---|
| 10% | $99 | −$1 | −$101 | −$201 | −$301 |
| 20% | $298 | $198 | $98 | −$2 | −$102 |
| 30% | $497 | $397 | $297 | $197 | $97 |

**Speaker notes:** Skimming dominates Penetration as long as conversion ≥ 10% and cost ≤ $400. Both well within industry norms for SaaS contract upgrades.

---

## Slide 8 — TASK 4: 7Ps — Closing the 1-Feature Trap

**Headline:** *Customers who adopt 1 feature churn at 46% — worse than non-adopters at 21%. The fix is process redesign.*

**Visual:** Feature adoption curve (bar chart) with annotation on the 1-feature peak; alongside the 30/60/90 onboarding flow diagram

**Process redesign — the central P:**
- **Day 0**: Signup
- **Day 30**: Setup walkthrough (target: +1 feature)
- **Day 60**: Value report (showing usage benefit; target: +1 feature)
- **Day 90**: Bundle upgrade offer (target: 3+ features → drops churn from 46% to 27%)

**Other 6 Ps** (briefly):
- Product: bundles for 3 personas (Basic / Pro / Enterprise)
- Price: bundle anchoring; segment-specific retention pricing
- Place: assisted onboarding for high-value segments
- Promotion: At-Risk High Spenders get retention pricing
- People: dedicated AM for High Value Loyalists
- Physical Evidence: progress dashboard + value reports

**Speaker notes:** 966 customers are stuck at 1 feature. If we save half of them via process redesign, that's ~280 retained customers and ~$340K in LTV savings.

---

## Slide 9 — Power BI Executive Roadmap (DAX Churn Probability)

**Headline:** *Operational tool: every customer scored daily, surfaced in Power BI via DAX.*

**Visual:** Screenshot mockup of the Power BI dashboard showing:
- Page 1 (Executive Overview): KPI strip, Tenure funnel, STP bubble, Decision Tree
- Page 2 (Customer Risk Detail): top-50 highest-risk customers, threshold slicer
- Page 3 (Customer 360): drill-through detail per customer

**Key DAX measures:**
- `Avg Churn Probability` = AVERAGE(churn_scores[churn_prob])
- `High Risk Count` = CALCULATE(COUNTROWS(churn_scores), churn_prob >= [Churn Threshold])
- `Revenue At Risk` = CALCULATE(SUM(monthly_charges), churn_prob >= [Threshold])
- `LTV Uplift Ratio` = LTV(2yr) / LTV(MTM) = 13.8x

**Speaker notes:** The Power BI dashboard runs daily. CSMs have a live high-risk customer list, sorted by churn probability, segmented by intervention type.

---

## Slide 10 — 12-Month Roadmap

**Headline:** *Sequenced rollout: stabilize, then optimize.*

| Phase | Days | Owner | Initiative | Projected impact |
|---|---|---|---|---|
| **Stabilize** | 0–60 | CPO | Deploy churn model + Power BI dashboard; CSM team trained | Visibility unlocked |
| **Save** | 30–90 | VP CS | Save campaign for At-Risk High Spenders (1,465 cust × 15% save × $750 LTV uplift) | $165K |
| **Skim** | 60–180 | CPO + CS | MTM → 2yr migration push (top quartile MTM, 1,000 × 20% × $1,990) | $398K |
| **Onboard** | 90–180 | CPO | 30/60/90 onboarding redesign (close 1-feature trap, 966 × 30% × $1,200) | $348K |
| **Friction** | 120–240 | CFO + CS | Payment migration (e-check → auto-pay, 2,365 × 5% × $500) | $59K |
| **TOTAL 12-MO** | | | | **$970K** |

---

## Slide 11 — Risks & Honest Call-outs

- **PivotCo is a synthetic anchor**: per-customer numbers are real (7,043 records from IBM's published Telco dataset); the $200M ARR firm-level figure is narrated for boardroom relevance.
- **Dataset is technically telecom**, not pure SaaS. Subscription mechanics are identical (recurring billing, contract tenure, feature add-ons, churn behavior), but a reviewer who knows the dataset will recognize this. We disclose it.
- **Skimming/Penetration in original brief refers to pricing**. We reframe as contract-strategy choice because the dataset has fixed pricing per service. EV-tradeoff structure is preserved.
- **Conversion rates are industry benchmarks**, not company-specific. PivotCo's actual conversion will determine real ROI.
- **The "1-feature trap" finding is observational, not causal**. Customers who adopt 1 feature may be a self-selecting group. A randomized A/B test on the onboarding intervention is recommended before full rollout.
- **The model AUC of 0.844** is good but not perfect. ~20% of high-risk-flagged customers won't actually churn (false positives). Save-campaign costs should account for this.

---

## Slide 12 — Recommendation

**Headline:** *Approve the Skimming roadmap. Start with the save campaign. Onboarding redesign in Q2.*

**Decision matrix:**
- **Approve now (Q1):** Power BI rollout + save campaign on At-Risk High Spenders
- **Approve for Q2:** Onboarding redesign (30/60/90 milestones)
- **Investigate:** The Fiber optic anomaly (41.9% churn despite premium pricing)

**Total expected impact (year 1):**
- Direct LTV uplift: **$970K**
- Reduced churn rate: 26.5% → 21% (target)
- DAX-powered Power BI in production = sustained operational visibility
- Process maturity: from no-churn-prediction to weekly CSM dashboard review

**The pivot:** *Stop trying to acquire faster. Start trying to keep customers longer.*

---

## Appendix Slide A — Deliverables Inventory

- `ProductPivot_Lifecycle.ipynb` — End-to-end Jupyter notebook (all 4 tasks + churn model)
- `ChurnPlaybook.xlsx` — Excel tool (8 sheets, 62 live formulas, Decision Tree EV + sensitivity)
- `churn_scorer.py` — Python CLI for batch churn probability scoring (logistic regression, AUC=0.844)
- `Power_BI_Roadmap_Spec.md` — Power BI build spec (5 pages, full DAX measure library)
- `sql/schema.sql` + `sql/load_data.py` — SQLite schema (4 tables, 6 analytical views)
- `Project_Brief_Reframed.md` — Reframed brief with full diff vs. original
- `README.md` — Workflow, methodology, honest call-outs
- `data/WA_Fn-UseC_-Telco-Customer-Churn.csv` — Source data
