# Track 2 — Workforce Risk Audit

**Attrition, Compensation & Retention Strategy** | IBM HR Analytics anchor | Product/Consulting track

---

## What's in this bundle

| File | Purpose |
|---|---|
| `Workforce_Audit.ipynb` | Analytics notebook — Compensation DuPont, logistic regression with multicollinearity check, 4-year cost forecast across 3 scenarios, 7 CSVs for Tableau |
| `Workforce_Audit_Engine.xlsx` | 8-sheet financial model — 161 formulas, all validated zero errors. Active Scenario picker (1/2/3) flips the entire model. |
| `Tableau_Dashboard_Spec.md` | Step-by-step build guide, 8 sheets + 3 dashboard actions including the brief's drill-through |
| `Pyramid_Deck_Outline.md` | 10-slide deck following Barbara Minto's pyramid: recommendation first, three pillars, evidence below |

---

## Folder layout for running this

```
Module 02/
└── Track 02/
    └── workforce_audit/
        ├── data/
        │   └── WA_Fn-UseC_-HR-Employee-Attrition.csv  ← place IBM CSV here
        ├── outputs/                                    (auto-created — 7 CSVs)
        ├── figures/                                    (auto-created — 4 PNGs)
        ├── Workforce_Audit.ipynb                      ← run this
        ├── Workforce_Audit_Engine.xlsx
        ├── Tableau_Dashboard_Spec.md
        ├── Pyramid_Deck_Outline.md
        └── README.md
```

Dataset: [IBM HR Analytics Employee Attrition](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset)

---

## Workflow

1. **Run the notebook** end-to-end (`Cell → Run All`). It produces 7 CSVs and 4 figures in ~10 seconds.
2. **Open the Excel engine.** Inputs are blue, formulas are black, scenario toggles are yellow. Edit the **Active Scenario** picker on the `Scenarios` sheet (cell C10) to flip between Baseline / Wage-Inflation / Retention-Investment.
3. **Build the Tableau dashboard** by following `Tableau_Dashboard_Spec.md`.
4. **Build the pitch deck** using `Pyramid_Deck_Outline.md` as a slide-by-slide skeleton.

---

## Headline findings

### The Audit's Hero Finding: It's Not Pay or Distance — It's OverTime

| Driver | Effect on attrition odds (per std-unit) | Notes |
|---|---:|---|
| **OverTime** (binary) | **× 1.88** | Strongest single driver. Nearly doubles attrition odds. |
| DistanceFromHome | × 1.27 | Real but modest. ~25% increase per std-unit (~8 km). |
| MonthlyIncome (controlling for JobLevel) | × 0.90 | **Pay's apparent effect is mostly a JobLevel confound.** Income & JobLevel correlate at r = 0.95. |
| JobLevel | × 0.75 | Higher seniority = lower attrition. The seniority effect, not the pay effect. |

**The brief's "Distance vs Pay" framing is a false dichotomy.** The correct answer is **OverTime, concentrated at JobLevel 1**.

### Compensation DuPont: Cost-per-Retained-FTE

The most-expensive role to retain isn't the highest-paid — it's the one with the worst retention multiplier.

| Role | Annual Pay | Retention Rate | Tenure Mult | **Cost per Retained FTE** | vs Baseline |
|---|---:|---:|---:|---:|---:|
| **Sales Representative** | $30,948 | 60.2% | 0.6× | **$128,436** | **2.14×** |
| Laboratory Technician | $34,632 | 76.1% | 0.7× | $76,032 | 1.27× |
| Sales Executive | $74,772 | 82.5% | 1.4× | $64,743 | 1.08× |
| Research Director | $198,120 | 97.5% | 3.6× | $56,425 | 0.94× |

Sales Reps cost **2.14× the baseline** to retain — driven by churn, not by pay.

### 4-Year Cost Forecast

| Scenario | 4-yr Cumulative | Δ vs Baseline |
|---|---:|---:|
| Baseline | $89.2M | — |
| **Wage-Inflation** | **$108.5M** | **+$19.2M** |
| **Retention-Investment** | **$87.9M** | **-$1.3M** (net of $5K/yr program cost) |

**The macro hedge is the dominant story.** Wage-Inflation costs $19M more than Baseline, while Retention-Investment saves $1.3M. The CHRO's most important lever is **proactive wage adjustment for retention-critical segments BEFORE inflation hits** — reactive raises during inflation are 14× more expensive than preemptive retention investment.

---

## Methodology notes

**Why three departments instead of three cities.** The original brief framed the project as a "Subscription Coffee" service deciding between three cities. We reframed around the IBM HR dataset's natural structure — three departments (Sales / R&D / HR) — because:
- The audit logic is identical (compare three units, recommend retention investment per unit)
- The dataset is real, not simulated
- The Pyramid Principle deck works the same way

**Compensation DuPont reframing.** Classic DuPont decomposes ROE into Net Margin × Asset Turnover × Equity Multiplier. The HR analogue we use is:

$$\text{Cost per Retained FTE} = \text{Pay per FTE} \times \frac{1}{\text{Retention Rate}} \times \frac{1}{\text{Tenure Multiplier}}$$

Just like ROE, this lets the CHRO see whether high cost is driven by pay, by churn, or by short tenure.

**Multicollinearity handling.** MonthlyIncome and JobLevel correlate at r = 0.95 — a textbook collinearity case. The notebook computes Variance Inflation Factor (VIF) explicitly, runs the regression with both variables, and interprets MonthlyIncome's coefficient as "pay premium within a job level" rather than "pay effect overall."

**Cost forecast assumptions** (all editable in the Excel `Inputs` sheet):
- Wage inflation: 4%/yr Baseline, 7%/yr Wage-Inflation
- Replacement cost multiplier: 1.5× annual salary (industry rule of thumb)
- Retention investment: $5K/yr per JobLevel-1 employee
- Target attrition with retention program: 15% (industry good-practice benchmark)

**Recommended actions for the CHRO:**

1. **Cap mandatory OverTime for JobLevel 1 staff** — the highest-leverage single intervention based on the regression
2. **Targeted retention bonuses for Sales Reps and Lab Technicians** — the two roles with disproportionate cost-per-retained-FTE
3. **Pre-emptive market-rate adjustment** for retention-critical segments to hedge the $19M Wage-Inflation downside
4. **Monthly attrition dashboard** review with the CHRO; quarterly review with the Executive Committee
