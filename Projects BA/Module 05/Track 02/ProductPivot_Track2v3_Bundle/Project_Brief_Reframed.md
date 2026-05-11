# 2. The Product & Consulting Track (Reframed)

**Project Title:** The Product Pivot: Data-Driven Lifecycle Optimization for SaaS Growth.

**Dataset:** [Telco Customer Churn (IBM) | Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) — 7,043 customers × 21 columns

**Scenario:** **PivotCo, a B2B subscription-services provider** (telecom-SaaS hybrid: phone, internet, security, backup, device protection, tech support, and streaming services bundled into a single recurring subscription, ~$200M ARR, ~7,043 active subscribers) is seeing **a 26.5% annual churn rate** with revenue exposure of **$139K/month** from at-risk customers (~$1.67M annualized, $4.45M LTV-style impact). User Retention is dropping fastest in the **first 6 months** (52.9% churn) and Feature Adoption is paradoxically worst among customers who adopt exactly one feature (45.8% churn vs. 21.4% for non-adopters). The Product Manager must decide whether to invest in **"Feature Enhancement"** (deeper engagement among high-adoption segments) or **"Market Expansion"** (acquiring more low-commitment month-to-month customers) using **Expected Value (EV)** logic.

**Objective:** Map the **Customer Journey funnel from Awareness (0-6mo) to Advocacy (49-72mo)**, identify attrition points using **MECE root-cause decomposition**, and use a **Decision Tree** to justify the next move in the product roadmap (Skimming = lock-in via annual/two-year contracts vs. Penetration = month-to-month volume play).

**Tasks:**

1. **User Behavior Analysis:** Use Python (pandas/seaborn) to quantify the Customer Journey from "Awareness" to "Advocacy" — **5-stage funnel using tenure buckets (0-6mo / 7-12mo / 13-24mo / 25-48mo / 49-72mo)**, with churn rate at each stage and identification of the largest attrition cliff (the 0-6mo stage absorbs **53% of churners**).

2. **Strategic Logic:** Use the **MECE Framework** to branch out the reasons for low retention into **(a) Contract Friction**, **(b) Payment Friction**, **(c) Service Quality**, **(d) Demographic Risk**, **(e) Feature Engagement Gap**. Perform **STP (Segmentation, Targeting, Positioning)** on **4 actionable segments**: High Value Loyalists / At-Risk High Spenders / Low Engagement Newcomers / Sticky Basics.

3. **Investment Choice:** Build a **Decision Tree in Excel** to calculate the Expected Value of two competing product strategies — **Skimming** (incentivize multi-year contract migration; per-customer EV of ~$2,145) vs. **Penetration** (defend month-to-month acquisition funnel; per-customer EV of ~$153). Include sensitivity analysis on retention-investment cost ($200-$500/customer) and conversion rate (10-30%).

4. **Pricing & Position:** Apply the **7Ps of Services** (Product, Price, Place, Promotion, People, Process, Physical Evidence) to redesign the product's value proposition and **"Process" flow** to improve user onboarding — specifically targeting the **"1-feature trap"** (where customers who adopt only one service feature churn at 45.8%, worse than non-adopters at 21.4%).

**Deliverable:** A **Power BI Executive Roadmap** with **DAX-calculated "Churn Probability"** (logistic regression scored per customer, surfaced as a DAX measure on the customer dimension) and a **strategic growth recommendation** quantified in dollars (recommend Skimming-led roadmap with projected $4.5M LTV upside).

---

## What Changed From the Original Brief

| Item | Original | Reframed | Why |
|---|---|---|---|
| Dataset | H&M Personalized Fashion Recommendations | IBM Telco Customer Churn (Kaggle blastchar) | H&M is B2C fashion retail with no churn, no feature adoption, no SaaS funnel — fundamentally wrong domain. Telco is a subscription-services dataset that maps to the brief task-by-task. |
| Industry framing | "B2B software company" | "B2B subscription-services provider (telecom-SaaS hybrid)" | Telecom subscription mechanics are identical to SaaS subscription mechanics: recurring billing, contract tenure, feature/service add-ons, churn. One-line reframe preserves the SaaS analytical playbook. |
| Funnel definition | Generic Awareness → Advocacy | 5 tenure buckets mapped to AAARRR-style stages (0-6mo Awareness/Activation, 7-12mo Engagement, 13-24mo Retention, 25-48mo Loyalty, 49-72mo Advocacy) | Concrete dimensions taken from the actual `tenure` field. Makes the funnel measurable. |
| Attrition cliff | Implicit | 0-6mo is the largest cliff: 52.9% churn at this stage; ~53% of all churners come from here | Specific, dramatic finding the data supports. |
| MECE branches | Implicit | Five branches: Contract Friction / Payment Friction / Service Quality / Demographic Risk / Feature Engagement Gap | Each branch has a clean data signal: contracts (15× churn variance), payment methods (3× variance), Internet service (5.7× variance), Senior status (+7pp), feature adoption (4× variance). |
| STP segments | Implicit | 4 named segments with quantified n / churn / monthly / LTV | Boardroom-ready, action-priority-ranked. |
| Skimming vs. Penetration | Pricing terms only | Reframed as contract-strategy choice: lock-in (skimming = 2-yr contracts) vs. volume-play (penetration = month-to-month) | The original Skimming/Penetration *pricing* concept doesn't fit a single-price-point dataset. Reframing as contract-strategy preserves the EV-tradeoff structure exactly. |
| 7Ps "Process" focus | Generic onboarding | Specifically targets the "1-feature trap" (adopting 1 feature = 45.8% churn vs. 21.4% for 0 features) | Uses the most counterintuitive finding in the data as the lever for the redesign. |
| DAX Churn Probability | DAX measure | DAX measure on logistic-regression scored probability + cohort-aware filtering | Specifies the DAX implementation rather than leaving it as hand-wave. |

**What stays unchanged:** DMAIC-adjacent structure (Define funnel → Measure attrition → Analyze MECE → Decide via EV → Roadmap), all four task areas, both deliverables (Power BI Executive Roadmap + strategic recommendation), the EV-driven decision logic.

---

## Continuity vs. Track 2 v1 (Workforce) and v2 (PremiumPivot)

| Aspect | Track 2 v1 (Workforce) | Track 2 v2 (PremiumPivot) | Track 2 v3 (Product Pivot — this build) |
|---|---|---|---|
| Framework | HR attrition analysis | Pricing elasticity / GMV optimization | SaaS lifecycle / churn / EV decision tree |
| Hero metric | OT Odds Ratio = 1.88, AUC = 0.748 | Elasticity = -0.106, $204.6M GMV | Two-year contract LTV uplift = 15× vs. MTM, $4.5M exposure |
| Dataset | IBM HR (real attrition) | Google Play (real apps) | IBM Telco Churn (real subscriptions) |
| Methodology | Logistic regression, OT scenarios | Demand elasticity, GMV simulation | Decision Tree EV, MECE, STP, 7Ps |
| Deliverable | Workforce strategy | GMV optimization model | Product roadmap + DAX churn probability |
| Audience | CHRO | Pricing/Product VP | Product Manager / CPO |

The deliberate choice across Track 2 versions: each version takes a fundamentally different "what does the data tell us about people-and-money decisions?" lens. Workforce = retention of employees; PremiumPivot = pricing power on apps; Product Pivot = retention of customers. Three orthogonal applications of the same underlying analytical discipline.
