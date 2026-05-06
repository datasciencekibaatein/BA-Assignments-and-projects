# EduTech Global · Market Entry Strategy
**Module 1 · Track 2 · Product & Consulting**

7 Jupyter notebooks producing the full deliverable pack: macro audit, workforce diagnostic, scenario model, break-even calculator, HR dashboard, and the final Market Entry Playbook PDF.

---

## Folder layout

The notebooks expect this structure:

```
Module 01/
└── Track 02/
    ├── dataset/
    │   ├── HR-Employee-Attrition.csv     (or WA_Fn-UseC_-HR-Employee-Attrition.csv — both work)
    │   └── macro_indicators.csv          (shipped in this zip)
    └── edutech/
        ├── 01_macro_entry_audit.ipynb
        ├── 02_workforce_analytics.ipynb
        ├── 03_attrition_visualisations.ipynb
        ├── 04_market_modeling_xlsx.ipynb
        ├── 05_constraint_management_xlsx.ipynb
        ├── 06_build_dashboard_xlsx.ipynb
        └── 07_market_entry_playbook.ipynb
```

When the notebooks run, they auto-create:
- `edutech/data/`     — intermediate CSVs
- `edutech/outputs/`  — final .xlsx, .pdf, and analytical CSVs
- `edutech/figures/`  — all .png charts

The notebooks **auto-resolve paths** — they walk up the tree to find the `edutech/` folder, then find `dataset/` as a sibling. No editing required.

---

## Run order

Run the notebooks **in numerical order**. Each one writes outputs that the next one reads.

| # | Notebook | Produces | Maps to brief |
|---|----------|----------|---------------|
| 01 | `01_macro_entry_audit.ipynb` | Attractiveness Index ranking, macro trend charts | **Task 1** |
| 02 | `02_workforce_analytics.ipynb` | Breaking-point analysis, top attrition drivers | **Task 2** |
| 03 | `03_attrition_visualisations.ipynb` | Heatmaps for the dashboard | Supports Deliverable 2 |
| 04 | `04_market_modeling_xlsx.ipynb` | `Market_Modeling.xlsx` — Best/Base/Worst scenarios | **Task 3** |
| 05 | `05_constraint_management_xlsx.ipynb` | `License_BreakEven_GoalSeek.xlsx` | **Task 4** |
| 06 | `06_build_dashboard_xlsx.ipynb` | `Workforce_Stability_Dashboard.xlsx` | **Deliverable 2** |
| 07 | `07_market_entry_playbook.ipynb` | `Market_Entry_Playbook.pdf` | **Deliverable 1** |

---

## Datasets

**1. IBM HR Attrition** (you already have this)
- File: `HR-Employee-Attrition.csv` (notebook also accepts the original `WA_Fn-UseC_-HR-Employee-Attrition.csv`)
- 1,470 employees · 35 features · 16% attrition
- Used as a stand-in for EduTech's internal HR data. Methodology applies identically to your real data with the same column names.

**2. World Bank macro indicators** (curated CSV, included in this zip)
- File: `macro_indicators.csv`
- 51 rows: GDP growth, CPI inflation, lending rate, internet penetration, Ease of Doing Business
- Countries: Brazil, Vietnam, Germany · Years: 2019–2023 (EDB is one-time, 2020 final edition)
- Source: World Bank Open Data — World Development Indicators (WDI) and Doing Business 2020
- Sourced columns include the original WDI indicator code so the data is fully traceable

**No API calls, no internet required, no extra `pip install` steps.** Pure offline pipeline.

---

## Headline findings (after running the pack)

- **Vietnam ranks #1** on the Attractiveness Index (75.9), ahead of Germany (50.0) and Brazil (35.2)
- **Internal attrition is 16.1%** — above the 10–15% B2B SaaS benchmark
- **Top 5 drivers**: OverTime, JobRole, MaritalStatus, TotalWorkingYears, JobLevel
- **Highest-risk segment**: 88 employees (6% of workforce) doing OverTime + tenure ≤ 2yr + Job Level ≤ 2 → **55.7% attrition rate** (3.5x company average)
- **Revenue scenarios**: Worst $864K · Base $900K · Best $1.01M (Year 1)
- **Break-even constraint**: a 5pp interest rate hike (10% → 15%) flips NPV from +$162K to -$200K. Goal Seek finds the new break-even at **~3,115 licenses** (3.8% lift over the 3,000-license baseline)
- **HR programme ROI**: $330K total annual cost → $5.2M annual saving from reduced attrition (≈ 16x return)

---

## Notes on framing

A few things worth knowing before the brief assessment:

- **Task 1's "Monopolistic vs Oligopolistic" framing**: macro indicators (GDP/CPI/rates) don't determine market structure on their own. Notebook 01 produces the macro Attractiveness Index, then adds a qualitative competitive-landscape table identifying the actual market structure per country (e.g., Vietnam = highly fragmented, Germany = oligopolistic).
- **The "Economic Indicators dataset"** mentioned in the brief doesn't exist as a downloadable file. We've curated the equivalent World Bank indicators into `macro_indicators.csv` with full source attribution.
- **Price elasticity** isn't in the IBM HR data (different domain). Notebook 04 uses documented industry-benchmark elasticities for B2B SaaS (-0.5 to -1.5 range, from Gartner / OpenView SaaS Benchmarks).
- **The IBM HR data is generic**, not EduTech-specific. The methodology is what matters — the notebooks document this caveat in the final PDF's "Methodology & Limitations" section.

---

## Goal Seek instructions (Notebook 05 deliverable)

`License_BreakEven_GoalSeek.xlsx` includes a README sheet with step-by-step instructions, but the short version:

1. Open the **Calculator** sheet
2. Note the NPV at default inputs (positive at 10% rate)
3. Change cell **B6** (Interest rate) from 10% to 15%
4. NPV turns negative
5. Go to **Data → What-If Analysis → Goal Seek**
6. Set cell: **B14** · To value: **0** · By changing cell: **B5**
7. Excel finds the break-even license count (~3,115)

The Sensitivity sheet shows the same answer across a license × rate grid, no Goal Seek needed.
