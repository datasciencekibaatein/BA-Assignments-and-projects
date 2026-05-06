# Pyramid Principle Deck Outline — Workforce Risk Audit

The Pyramid Principle structure: **lead with the recommendation**, then support with three pillars, each backed by evidence. Reading time: 3 minutes; presentation time: 12-15 minutes.

---

## Slide 1 — Title

> **Workforce Risk Audit**
> *Where to invest retention dollars first*
>
> Prepared for the CHRO | IBM HR Analytics

Footer: Date, presenter, "Confidential — Internal use only"

---

## Slide 2 — The Recommendation (Pyramid Top)

> **Cap mandatory OverTime for JobLevel 1 staff and reinvest the savings into targeted retention bonuses for Sales Representatives and Lab Technicians.**
>
> **Expected impact:** 4-year cumulative attrition cost reduced from $89M (Baseline) to $87M (Retention-Investment). Net savings: $1.7M after the $5K/employee/year program cost. **More importantly, this protects against the $19M downside under a Wage-Inflation scenario.**

This is the only slide the executive needs to read. Everything else supports this claim.

---

## Slide 3 — The Three Supporting Pillars (Pyramid Middle)

A single slide with three columns:

| Pillar 1: Diagnostic | Pillar 2: Causal | Pillar 3: Financial |
|---|---|---|
| **Where is the bleeding?** | **Why is it bleeding?** | **What does it cost?** |
| Sales Rep & Lab Tech roles bleed talent at 40% and 24%. JobLevel 1 attrition is 26.3% across all departments. | OverTime (not pay, not distance) is the strongest predictor. OverTime nearly doubles attrition odds. Pay's effect is largely a JobLevel confound. | $89M cumulative 4-year baseline cost. Wage-Inflation scenario adds $19M. Retention investment saves $1.7M net and hedges the macro downside. |
| Slide 4 detail | Slide 5 detail | Slide 6 detail |

---

## Slide 4 — Pillar 1 Detail: Diagnostic

**Title:** "Where is the bleeding? — JobLevel 1 across two roles."

**Visual (left half of slide):**
- Horizontal bar chart from `figures/attrition_by_role.png`
- Sales Rep (40%) and Lab Tech (24%) marked in red
- Research Director (2.5%) marked in green at the bottom

**Right half:**
- Three bullet takeaways:
  - **40% of Sales Reps leave each year** — 33 of 83 employees
  - **24% of Lab Technicians leave each year** — 62 of 259 employees
  - **JobLevel 1 attrition is 26.3% across all departments** — entry-level is the structural issue

**Footer caption:** "n = 1,470 employees, 9 job roles. Source: IBM HR Analytics."

---

## Slide 5 — Pillar 2 Detail: Causal

**Title:** "Why is it bleeding? — OverTime, not Pay or Distance."

**Visual (top):**
- Horizontal bar chart of standardised logistic regression coefficients
- OverTime bar at +0.63 in red (largest positive)
- Distance bar at +0.24 in lighter red
- MonthlyIncome bar at -0.10 in light green (small)
- JobLevel bar at -0.29 in green
- Age bar at -0.30 in green

**Below (the multicollinearity callout):**
- "**MonthlyIncome and JobLevel correlate at r = 0.95.** The brief's framing of 'Distance vs Pay' as the key drivers is a false dichotomy. Once we control for JobLevel, Pay's residual effect is small."
- "**OverTime nearly doubles attrition odds** (OR = 1.88 per std-unit) — three times the effect of Distance."

**Footer:** "Logistic regression, AUC = 0.748 out-of-sample. n = 1,470."

---

## Slide 6 — Pillar 3 Detail: Financial

**Title:** "What does it cost? — $89M baseline, $108M under inflation, $87M with retention spend."

**Visual:**
- Line chart from `figures/attrition_cost_forecast.png` (3 scenarios over 4 years)
- Highlighted box: "Cumulative 4yr savings: Retention-Invest vs Baseline = $1.7M"
- Second highlighted box: "Cumulative 4yr macro risk: Wage-Inflation vs Baseline = +$19M"

**Below:**
- Two tables side-by-side:

**Cost-per-Retained-FTE (Top 3 most expensive roles):**
| Role | Cost per Retained | vs Baseline |
|---|---:|---:|
| Sales Rep | $128K | 2.14× |
| Lab Tech | $76K | 1.27× |
| HR | $52K | 0.87× |

**4-Year Cumulative Cost by Scenario:**
| Scenario | 4-yr Total | Δ vs Baseline |
|---|---:|---:|
| Baseline | $89M | — |
| Wage-Inflation | $108M | +$19M |
| Retention-Investment | $87M | -$2M |

---

## Slide 7 — Implementation: 90-Day Playbook

A single-slide implementation roadmap. Three columns, each a phase:

| Phase 1: Days 1-30 | Phase 2: Days 31-60 | Phase 3: Days 61-90 |
|---|---|---|
| **Stop the bleeding** | **Build the program** | **Measure & iterate** |
| - Cap mandatory OT at 5 hrs/week for JL-1 | - Design retention bonus structure ($5K/yr/JL-1) | - Monthly attrition dashboard review |
| - Audit current OT distribution | - Identify Sales Rep & Lab Tech mentors | - Quarterly Cost-per-Retained reporting |
| - Communicate policy change | - Launch fast-track promotion paths | - Re-run logistic regression at 12 months |

Owner per phase: HRBP (P1), Comp & Benefits (P2), HR Analytics (P3).

---

## Slide 8 — Risks & Mitigations

A single-slide risk register:

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| OT cap reduces Sales Rep deal capacity | Medium | High revenue | Phase the cap; offer commission rebalancing |
| Retention bonuses misallocated to non-flight-risk staff | Medium | Wasted $$ | Use the dashboard's risk-bucket flag (OT×JL1 = High Risk) |
| Wage-inflation forces reactive raises anyway | High | +$19M | Pre-emptive market-rate adjustment for Sales Rep & Lab Tech BEFORE inflation hits |
| 12-month measurement period too short | Low | Wrong conclusion | Combine with logistic regression coefficient stability tracking |

---

## Slide 9 — The Ask

> **We are asking the Executive Committee to approve:**
>
> 1. **Policy change:** Mandatory OT cap of 5 hrs/week for JobLevel 1, effective Q1 next year.
> 2. **Budget allocation:** $1.6M/year retention investment ($5K × 312 JobLevel-1 employees).
> 3. **Reporting commitment:** Monthly attrition dashboard delivered to CHRO; quarterly review with the EC.
>
> **Decision needed by:** [Date].
> **Owner:** CHRO, supported by HR Analytics and Comp & Benefits.

---

## Slide 10 — Appendix Index

A single slide listing the appendix contents (all backup material):

- Appendix A: Full attrition table by Department × JobRole × JobLevel
- Appendix B: Logistic regression — full coefficients, VIF, ROC curve
- Appendix C: Compensation DuPont — all 9 roles
- Appendix D: 4-year forecast model — full assumptions table
- Appendix E: Sensitivity analysis — cost vs Wage Inflation × Replacement Multiplier
- Appendix F: Methodology and data sources

---

## Pyramid Principle structural notes

This deck follows Barbara Minto's pyramid:

- **Top (Slide 2):** Single-sentence governing thought.
- **Middle (Slide 3):** Three MECE supporting reasons (Diagnostic / Causal / Financial). Each reason is itself a complete idea.
- **Bottom (Slides 4-9):** Evidence and operational detail supporting each pillar.

The "appendix" slides (10+) are *not* part of the pyramid — they are reference material the audience can ask for. The first 9 slides should stand alone for a 12-minute board read.

**Key rules followed:**
1. **Lead with the answer.** No build-up. The recommendation is on Slide 2.
2. **Three pillars, not five.** Easier to remember.
3. **MECE.** The three pillars (Where/Why/Cost) don't overlap and cover the full brief.
4. **Numbers in the headline.** "Cap OT for JL-1" alone is a slogan; "saves $1.7M, hedges $19M downside" is a recommendation.
5. **The Ask is unambiguous.** Slide 9 names the decision needed and the owner.
