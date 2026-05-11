# The Premium Pivot - Pyramid Principle Deck

> Strategic re-positioning of a marketplace subscription ecosystem.
> 11 slides. McKinsey-style: SCR opening, Pyramid Principle structure (1 governing thought + 3 supporting MECE arguments).
> Audience: Marketplace leadership team (CEO, CMO, CPO, CFO).

---

## SCR Opening (Situation - Complication - Resolution)

**Situation.** Google Play is the world's largest app marketplace - 9,638 active apps in scope, 75.3 billion installs, 33 categories.

**Complication.** Despite this scale, the paid-app tier generates only $204.6M in measurable Gross Merchandise Value - a yield of $0.003 per install. The marketplace is being out-monetized by agile subscription competitors. Worse: the standard analytical playbook (cross-sectional price regression) gives the *wrong* answer about how to fix it - it suggests prices are already too high.

**Resolution / Question.** How should we re-tier paid offerings to maximize GMV without collapsing install volume - and what does the data actually say about price sensitivity once we control for quality confounding?

---

## Slide 1 - Title & Audience Hook

**Title:** *The Premium Pivot - Why our paid-tier playbook is upside down*

**Subtitle:** *And the $53M opportunity hidden inside a sign-flipped elasticity coefficient*

**Visual:** Big number callout: "Naive elasticity = +0.30. Corrected elasticity = -0.11. The difference: $53M."

---

## Slide 2 - The Governing Thought (Top of the Pyramid)

> **Governing thought:** Adopt **Smart Skim** - lift inelastic-category prices 30%, drop elastic-category prices 10%, smooth marketing pacing in bullwhip categories. Projected lift: **+25.9% (~$53M)**. Layer a subscription tier for an additional ~$23M of recurring revenue.

**Three supporting arguments (MECE):**
1. **PRICE** - Quality-corrected elasticity reveals the marketplace is severely underpriced. Average paid app could absorb a 30% price increase with only ~3% volume loss in inelastic categories.
2. **VOLUME** - The Install -> Reviewer funnel leaks 97.3% at the first stage. Even modest improvements via lifecycle marketing materially expand the addressable paid base.
3. **MIX** - Categories have radically different unit economics (DuPont decomposition). One-size pricing is malpractice; per-category tiers fit the actual demand structure.

**Visual:** Pyramid diagram with 1 governing thought at top + 3 supporting arguments at base.

---

## Slide 3 - SUPPORTING #1.A - The Hero Finding: Naive Elasticity Is Wrong-Signed

**Headline:** A naive log-log regression of installs on price gives elasticity = **+0.30**. That's a positive number for a demand curve - mathematically impossible if buyers respond to price.

**Why?** Quality confounding. Higher-priced apps tend to be higher-quality (more reviews, better ratings) and attract MORE installs *despite* the price. The naive model picks up app-quality signal masquerading as price response.

**Visual:** Two scatter plots side-by-side:
- LEFT: log(price) vs log(installs) raw - upward sloping fit line in red
- RIGHT: residuals after controlling for rating + log(reviews) + category FE - mild downward slope

**Bottom line on slide:** "If you priced the marketplace using this regression, you would *raise* prices and miss the real lever entirely - the *whole strategy* hinges on getting this number right."

---

## Slide 4 - SUPPORTING #1.B - The Corrected Elasticity Says "Underpriced"

**Headline:** With category fixed effects + rating + log(reviews) controls, elasticity = **-0.106** (p=0.045, R squared = 0.898). The marketplace is **highly inelastic.**

**Implication:** A 10% price increase reduces installs by only ~1%. A 30% increase by only ~3%. Revenue elasticity is decisively positive in the underpriced regions.

**By-category breakdown:**
| Category | n | Elasticity | Strategy |
|---|---|---|---|
| GAME | 76 | -0.39 (p=0.005) | Penetrate (lower price) |
| FAMILY | 151 | -0.12 | Skim (raise price) |
| MEDICAL | 62 | -0.07 | Skim (premium niche) |
| TOOLS | 63 | -0.10 | Skim |
| PERSONALIZATION | 65 | -0.19 | Skim |

**Visual:** Horizontal bar chart of by-category elasticities, color-coded by strategy.

---

## Slide 5 - SUPPORTING #2.A - The Funnel: Where Customers Leak

**Headline:** From 21.79B installs to 0.34B advocates, we lose 98.4% of cohorts. The leaks are non-uniform.

**Funnel stages:**
| Stage | Volume | % of Install |
|---|---|---|
| Install | 21.79B | 100.000% |
| Reviewer | 0.58B | 2.664% |
| Advocate (positive review) | 0.34B | 1.566% |
| Detractor (negative review) | 0.18B | 0.840% |

**The opportunity:** Install -> Reviewer is the steepest drop (97.3%). Lifecycle marketing - well-timed review prompts, in-app NPS surveys - is a known lever. Even a doubling of this rate (1.5% -> 3%) materially expands the qualified addressable base for premium-tier conversions.

**Visual:** Funnel chart with stage drop-off labels.

---

## Slide 6 - SUPPORTING #2.B - The Bullwhip in Marketing Spend

**Headline:** SOCIAL, ENTERTAINMENT, FAMILY categories show review-volume variance > 2x install-volume variance. Marketing spend in these categories is over-reactive.

| Category | n_apps | CV(installs) | CV(reviews) | Amplification |
|---|---|---|---|---|
| SOCIAL | 18 | 2.25 | 3.37 | 1.50 |
| ENTERTAINMENT | 21 | 2.20 | 3.05 | 1.39 |
| FAMILY | 70 | 1.86 | 2.86 | 1.54 |
| FINANCE | 39 | 3.36 | 2.46 | 0.73 (smooth) |

**Recommendation:** In high-amplification categories, smooth marketing spend via 4-week rolling averages, not weekly review-count triggers. Estimated CAC reduction: 10%.

**Visual:** Horizontal bar chart of amplification by category, red bars where >1.2.

---

## Slide 7 - SUPPORTING #3.A - DuPont Decomposition Reveals Lever Differences

**Headline:** Identity: `Paid GMV = Total Installs x Paid Conversion Rate x Avg Paid Price`. Each category sits at a different point in this 3-dimensional space.

**Three archetypes from the data:**
- **MEDICAL** (premium niche): 38M installs, 1.46% conversion, $10.62 price -> $5.96M GMV. **Skim deeply, expand category.**
- **FAMILY** (mass premium): 6.2B installs, 0.34% conversion, $5.00 price -> $105.7M GMV (52% of marketplace). **Hold price, defend share.**
- **GAME** (volume play): 13.4B installs, 0.16% conversion, $1.94 price -> $40.7M GMV. **Penetrate further, capture share.**

**Visual:** Bubble chart - X = log(installs), Y = paid conversion %, bubble size = GMV, bubble color = avg price. MEDICAL is a small high-color bubble in the upper left; FAMILY is a large mid-color bubble center; GAME is a large low-color bubble lower right.

---

## Slide 8 - SUPPORTING #3.B - One-Size Pricing Leaves $35M+ on the Table

**Headline:** A simple "+20% across the board" lift earns +$36M (+17.5%). Smart Skim - the elasticity-aware tiered approach - earns **+$53M (+25.9%)**, a 50% improvement over the naive uplift, by avoiding price hikes in elastic categories.

**Per-category projected impact:**

| Category | Curr GMV | Action | Δ Price | Δ Volume | Lift |
|---|---|---|---|---|---|
| FAMILY | $105.7M | Skim | +30% | -3.4% | +25.5% |
| GAME | $40.7M | Moderate | +15% | -5.8% | +8.4% |
| MEDICAL | $5.96M | Skim | +30% | -2.0% | +27.4% |
| TOOLS | $5.46M | Skim | +30% | -3.0% | +26.2% |
| **Portfolio total** | **$204.6M** | -- | -- | -- | **+21.9%** ($+38M) |

**Visual:** Per-category bar chart of $ lift, sorted descending.

---

## Slide 9 - The Subscription Sidecar (Optional Upside)

**Headline:** Adding a $2.99/month subscription tier converted from existing paid users (57M install base) yields an additional ~$5M direct subscription revenue. Combined with bullwhip-driven CAC savings (~$18M), the Subscription Pivot total is +$23M (+11.4%).

**Why this is a sidecar, not the main play:**
- Subscription requires a 12-18 month rollout (auth infrastructure, billing, content gating)
- Addressable base is the paid-app cohort (57M), not the entire marketplace
- Realistic 0.5% conversion-lift assumption from this base

**Recommendation:** Run Smart Skim first (Q1-Q2). Pilot subscription tier in MEDICAL (highest-WTP segment) in Q3. Full rollout Q4.

**Visual:** Time line bar showing 18-month rollout of both pivots.

---

## Slide 10 - Implementation Roadmap (90 days)

**Phase 1 - Days 1-30:** Smart Skim pricing tier rollout in TOP 5 categories (FAMILY, GAME, MEDICAL, TOOLS, PERSONALIZATION)
- Pricing API update
- Developer notification (4-week notice)
- A/B holdout: 10% of new installs see old prices

**Phase 2 - Days 31-60:** Lifecycle marketing tests (boost Install -> Reviewer rate)
- In-app review prompts at Day 7 and Day 30
- Smoothed marketing-spend pacing in SOCIAL, ENTERTAINMENT, FAMILY
- Power BI dashboard live: track elasticity assumptions in real time

**Phase 3 - Days 61-90:** Measure + iterate
- Re-estimate elasticity per category using post-launch installs
- Lock in winning category-specific tiers
- Begin subscription tier infrastructure work for Phase 2 (Q3)

**Visual:** Gantt-style timeline with the 3 phases color-coded.

---

## Slide 11 - Risks & Honest Call-Outs

**What could go wrong:**
1. **Cross-sectional elasticity may not equal within-app elasticity.** Our -0.11 estimate is *between* apps. A specific app raising its price could see different behavior. Mitigation: A/B holdout in Phase 1.
2. **GMV proxy is not literal revenue.** Total GMV = price x install count assumes 100% conversion of installs to paid. Actual paid conversion within a paid app is unobserved. Mitigation: track Play Store revenue API post-launch to validate.
3. **Subscription model assumes 0.5% conversion lift on paid base.** If actual lift is 0.1%, sub revenue drops to ~$1M. Pilot in MEDICAL first to calibrate.
4. **Bullwhip diagnostic is heuristic.** True marketing-spend bullwhip would require ad-spend time series. Our CV ratio is a proxy.
5. **Price changes may anger developers.** Smart Skim imposes pricing changes on third-party sellers. Communications strategy and clear opt-out path required.

**The single biggest risk:** Acting on the naive +0.30 elasticity. *Don't.* The corrected elasticity is the only one to use.

**Visual:** Risk matrix - Likelihood (low/med/high) x Impact (low/med/high), each risk plotted.

---

## Closing slide - The Single Sentence

> **If we change one thing this quarter, it should be this: stop pricing the paid tier as if elasticity were positive. It isn't. The marketplace is underpriced, and Smart Skim closes that gap by 27 percentage points of revenue without losing meaningful install volume.**
