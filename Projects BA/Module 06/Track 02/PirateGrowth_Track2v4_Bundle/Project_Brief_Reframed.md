# Track 2 v4 — Project Brief Reframed

## 2. The Product & Consulting Track

**Project Title:** The Pirate's Growth Strategy: Scaling a Digital Ecosystem through Unit Economics.

**Dataset:** [Online Retail II | UCI ML Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii)

**Scenario:** A mid-market e-commerce platform (subscription-like repeat-purchase model) is concerned about high projected Customer Acquisition Cost as it scales. The board wants a recommendation on whether to implement **Dynamic Pricing** or a **Referral Loop (Virality)** to improve LTV/CAC. Underlying issue: only **23.6% of signups** activate (2nd purchase within 30 days), so the funnel itself is leaking before any acquisition strategy can pay off.

**Objective:** Quantify the AARRR funnel on real transaction data, compute LTV/CAC, run a 2-firm Nash equilibrium on penetration pricing, and use a Decision Tree EV calculation to pick between Pricing and Referral arms.

**Tasks:**

1. **Growth Framework:** Quantify the Conversion Funnel using **AARRR (Pirate Metrics)** on 5,878 customers across 24 monthly cohorts. Identify where the biggest drop-off occurs (Activation 76.4% drop vs Retention M+1 78.8% drop — close call, both addressed in MECE roadmap).

2. **Advanced Analytics:** Cohort retention heatmap (24 cohorts × 25 months) plus **Apriori-style Market Basket Analysis** on top-50 products. Top rule lift = 7.40x (Choc ↔ Tea hot water bottles); mean lift top-5 = 6.52x.

3. **Market Strategy:** **Game Theory (Nash)** on a 2-firm penetration pricing game (Hold / Cut 7% / Cut 15%); identify the Nash equilibrium and Pareto-optimal outcomes. Apply **STP math** — RFM segmentation into 6 segments + geographic targeting (International £5,709/cust = 2.07x UK).

4. **Storytelling:** Pyramid Principle deck (13 slides, SCR opening). Decision Tree EV with two arms: Dynamic Pricing (3 scenarios) vs Referral Loop (3 k-factor scenarios). Winner: Referral Loop EV £719,700/yr beats Pricing EV £47,865/yr by 15x.

**Deliverable:** A **Power BI-style Growth Command Center** (Excel workbook with explicit DAX measures: LTV, CAC, LTV/CAC, Activation, Retention, k-factor) plus a **MECE Roadmap** (6 months, 3 mutually exclusive workstreams: Virality / Activation / Retention).

---

## Differences from original brief

| Aspect | Original brief | Reframed brief (v4) |
|---|---|---|
| Dataset | H&M Personalized Fashion Transactions (Kaggle, gated) | Online Retail II (UCI, public) |
| Why changed | H&M has no signup events, no funnel, no referral data, no acquisition channels — fails Tasks 1, 3a, 4 | Online Retail II natively supports AARRR funnel via first/2nd purchase events; cohort retention via timestamps; basket analysis via invoice-level baskets |
| Industry framing | "mid-market SaaS provider" | "mid-market e-commerce platform (subscription-like repeat-purchase)" — honest framing; same unit economics math |
| Pirate funnel | "Activation vs Retention" abstract | Quantified: Activation 23.6% (≤30d), 46.7% (≤90d); Retention M+12 18.2% — biggest leak is Activation |
| Cohort analysis | "Power BI/Python" | 24 monthly cohorts with retention curves; best cohort 37.6% at M+12 |
| Market Basket | "cross-selling opportunities" | 19,347 multi-item baskets analyzed; top lift 7.40x; mean lift top-5 6.52x |
| Game Theory | "Nash equilibrium" abstract | 2-firm 3-strategy game with calibrated competitor; Nash = (Cut 15%, Cut 15%) at £16.24M each; Pareto = (Hold, Hold) at £17.50M each — prisoner's dilemma |
| STP | "high-value niche" | RFM 6 segments; Champions 1,814 cust = £13.5M LTV; International 2.07x UK rev/cust |
| Decision Tree EV | "expansion EV" | Two-arm tree: Pricing 3 scenarios EV=£47,865; Referral 3 scenarios EV=£719,700; ratio 15x |
| Power BI deliverable | "DAX for LTV/CAC" | 11-sheet Excel workbook with 58 formulas, 26 defined names, 15 explicit DAX measures ready to lift into .pbix |
| MECE Roadmap | "MECE framework" | 6-month plan, 3 workstreams (W1 Virality P0 £50K→£720K; W2 Activation P1 £30K→£180K; W3 Retention P2 £25K→£208K); ROI 10.6x |

---

## Continuity vs prior Track 2 versions

| Track | Hero method | Hero metric | Hero $ |
|---|---|---|---|
| Track 2 v1 (IBM HR) | Logistic regression | Attrition 16.12% | $1.4M attrition cost |
| Track 2 v2 (Google Play) | Elasticity + premium pivot | Elasticity −0.106 | $204.6M GMV |
| Track 2 v3 (IBM Telco) | Churn + EV decisioning | Churn 26.5%, AUC 0.844 | $970K 12-mo |
| **Track 2 v4 (Online Retail II)** | **AARRR + LTV/CAC + Nash + EV tree** | **Activation 23.6%, M+12 18.2%, lift 7.40x** | **£17.7M revenue, EV(Referral) £720K/yr** |

Four genuinely different consumer/subscription analytics lenses: workforce risk → premium pivot → product pivot → growth strategy.
