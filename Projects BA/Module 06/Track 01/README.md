# Track 1 v4 — Agile SPC Audit

**Operational Excellence: Eliminating Fulfillment Variance through DMAIC and Agile**

Dataset: DataCo Smart Supply Chain (180,519 orders, 2015-01-01 → 2018-01-31)

---

## Workflow

1. **Open `BRD_AgileSPC_Workbook.xlsx`** — 8-sheet workbook with the full BRD, FRs, SPC chart, EOQ calculator, Reorder alert engine, sprint backlog, and Tableau spec.
2. **Open `AgileSPC_Audit.ipynb`** — full Python pipeline: load data → BPMN-aligned analysis → 3NF SQLite + complex joins → X-bar SPC → EOQ + Safety Stock + Reorder Alert demo.
3. **Read `Project_Brief_Reframed.md`** for the rationale on why DataCo replaces Instacart and what's different from prior versions.
4. **Read `Strategic_Recommendation.md`** for the 13-slide Pyramid deck outline (the "tell the boss" version).
5. **Run `python scripts/spc_runner.py --input data/DataCoSupplyChainDataset.csv`** for a CLI version that regenerates SPC + EOQ outputs.

---

## Headline findings

| Finding | Number |
|---|---|
| Late deliveries (overall) | 54.83% |
| First Class late | 95.3% (systemic SLA failure — every order late by exactly 1 day) |
| Standard Class weekly subgroups analyzed | 162 |
| Out-of-control weeks (Special Cause) | **7 (4.3%)** |
| Common Cause σ̄ | 1.42 days |
| EOQ rollout savings (cross-category, 10 cats) | **$294,510 / year** |
| Top single-category EOQ saving | Fishing $64,785 (driven by $400 unit price) |
| Year-1 ROI estimate | >$650K at <$200K implementation |

---

## Methodology notes

### SPC: subgroup choice and control limits
- **Mode chosen:** Standard Class (107K orders) — the only mode with non-degenerate variance to analyze. First Class has σ=0 (every order late by exactly 1 day, no statistical variability), Same Day has σ=0.5 (binary).
- **Subgroup:** weekly, n≥30 filter applied → 162 weeks usable.
- **Method:** X-bar with s-bar control limits. For large n (median 708) we use the asymptotic A₃ ≈ 3/√n since the Bias-correction constant c₄ → 1.
- **Decision rule:** Western Electric Rule 1 (any point outside ±3σ). Rule 2 (9 consecutive points one side of CL) checked, max run = 5, no violation.

### EOQ: assumptions
- **Order cost (S):** $50/PO — industry-standard benchmark for e-commerce mid-cap.
- **Holding cost rate:** 25% of unit price annually — covers warehouse, capital, obsolescence.
- **Service level Z:** 1.65 (95% in-stock target) — chosen to match e-comm peer benchmarks.
- **Safety stock formula:** SS = Z × √(L̄·σ_d² + d̄²·σ_L²) — accounts for **both** demand variability and lead-time variability, which a pure σ_d-only SS would understate.
- **Status quo baseline:** quarterly ordering (Q = D/4) — typical legacy pattern; this is the inefficiency EOQ replaces.

### 3NF schema
- **Fact:** fact_fulfillment (180,519 rows, 12 measures incl. variance_days, late_flag, sales).
- **Dimensions (6):** dim_customer, dim_product, dim_category, dim_department, dim_region, dim_ship_mode.
- **Indexes:** customer_id, product_id, ship_mode_id, category_id.
- **Hero query:** `SELECT mode × category, COUNT(*), SUM(late_flag) FROM fact JOIN dim_ship_mode JOIN dim_category GROUP BY mode, category` — produces the late% heatmap visualization.

---

## Honest call-outs

1. **First Class "95.3% late" is structurally different from the other modes.** Every First Class order is late by exactly 1 day with σ=0. This isn't statistical variance to control — it's an SLA configuration error (scheduled = 0 days for a service that physically takes 1 day to ship). The fix is not SPC; it's renegotiating the published carrier SLA. We separate this from the SPC analysis explicitly.

2. **The "+15% spike in late deliveries" claim from the original brief is a story device.** The DataCo data covers 2015-01 to 2018-01 with the late% running steadily at ~55%. Time-series decomposition shows no specific 15% spike — the 55% level is the steady state. We frame this honestly in the BRD as "the level is 55%, the spike framing is rhetorical."

3. **EOQ savings of $294K assume the status-quo baseline is quarterly ordering.** If the company already orders monthly or bi-weekly, savings are smaller. Sensitivity analysis: at monthly status quo, savings drop to ~$110K; at bi-weekly, to ~$45K. Real number depends on a baseline audit in Sprint S0.

4. **The 7 Special Cause weeks have not been root-caused.** SPC tells us they exist; investigating them (via 5 Whys per week, with timestamped operational logs) is the actual Sprint S2 work. This deliverable identifies the question; it doesn't pre-answer it.

5. **The Excel workbook shows a 30-week sample of SPC data with 2 OOC for visual representativeness.** The full 162-week analysis (7 OOC) lives in `outputs/spc_weekly.csv` and is reproduced in the notebook.

---

## Continuity vs prior tracks on this dataset

This is the third orthogonal lens on DataCo. The intentional differentiation:

| Lens | v1 LastMile | v3 LeanShield | **v4 Agile SPC** |
|---|---|---|---|
| Hero method | SARIMA forecasting | DMAIC 5-step | **X-bar SPC + Agile** |
| Lead metric | OEE 53% / MAE 2.2 | First Class 95.3% late | **Special Cause weeks 4.3%** |
| EOQ angle | none | First Class only ($50K) | **Cross-category ($294K)** |
| Process map | none | Value Stream Map | **BPMN 2.0 Swimlane** |
| Hero deliverable | Tableau + forecast nb | DMAIC scorecard | **BRD + Sprint Backlog** |
| Stats hero | time-series fit | DMAIC measure phase | **Common vs Special Cause** |

A portfolio reviewer reading all three should see: "same dataset, three genuinely different analytical philosophies — predictive, diagnostic, and prescriptive."

---

## Files

```
AgileSPC_Track1v4_Bundle/
├── AgileSPC_Audit.ipynb              # 19 cells, executes clean
├── BRD_AgileSPC_Workbook.xlsx        # 8 sheets, 213 formulas, 13 defined names
├── Project_Brief_Reframed.md         # rationale + diff vs original
├── Strategic_Recommendation.md       # 13-slide deck outline
├── README.md                         # this file
├── data/
│   └── DataCoSupplyChainDataset.csv  # source data
└── scripts/
    └── spc_runner.py                 # CLI for SPC + EOQ pipeline
```
