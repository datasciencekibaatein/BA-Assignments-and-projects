# Track 1 — Last-Mile Delivery Audit

**Optimizing the "Last-Mile": A Predictive Audit of Delivery Volatility** | DataCo Global anchor | Analyst track

---

## What's in this bundle

| File | Purpose |
|---|---|
| `Last_Mile_Audit.ipynb` | Analytics notebook — connects to the SQLite DB, runs the OEE complex join, fits SARIMA, builds SPC p-charts, runs hypothesis tests |
| `sql/schema.sql` | 3NF schema (PostgreSQL-flavored, SQLite-compatible) — 10 tables + 4 analytical views |
| `sql/ER_Diagram.md` | Mermaid ER diagram + design rationale + row counts |
| `sql/load_data.py` | Loads the source CSV into a SQLite database following the schema |
| `Tableau_Dashboard_Spec.md` | Step-by-step dashboard build guide with the brief's drill-through actions |

---

## Folder layout for running this

```
Module 01/
└── Track 01/
    └── last_mile_audit/
        ├── data/
        │   ├── DataCoSupplyChainDataset.csv      ← place source CSV here
        │   └── dataco.db                          (auto-created by load_data.py)
        ├── outputs/                                (auto-created by notebook — 11 CSVs)
        ├── figures/                                (auto-created — 5 PNGs)
        ├── sql/
        │   ├── schema.sql
        │   ├── load_data.py
        │   └── ER_Diagram.md
        ├── Last_Mile_Audit.ipynb
        ├── Tableau_Dashboard_Spec.md
        └── README.md
```

Dataset: [DataCo Smart Supply Chain](https://www.kaggle.com/datasets/shashwatwork/dataco-smart-supply-chain-for-big-data-analysis) (also bundled in the existing Track-1 Module).

---

## Workflow

1. **Build the database**: `python3 sql/load_data.py` — creates `data/dataco.db` (~38 MB) following the 3NF schema. Takes ~30 seconds.
2. **Run the notebook** end-to-end (`Cell → Run All`). It produces 11 CSVs and 5 figures in ~30 seconds.
3. **Build the Tableau dashboard** by following `Tableau_Dashboard_Spec.md` — every sheet, calculated field, and dashboard action is specified with the exact numbers to verify against.

---

## Headline findings

### The Audit's Hero Finding: OEE by Shipping Mode

| Mode | Volume | SLA | Actual | OEE | Diagnosis |
|---|---:|---:|---:|---:|---|
| **Standard Class** | 39,324 | 4d | 4.0d | **52.9%** | Well-calibrated baseline |
| Same Day | 3,571 | 0d | 0.5d | 26.5% | Mostly hits same-day target |
| Second Class | 12,778 | 2d | 4.0d | 13.0% | **2-day SLA, 4-day actual** — broken |
| **First Class** | 10,079 | 1d | 2.0d | **2.2%** | **1-day SLA, 2-day actual, 95% late** |

**The problem isn't fleet capacity. The problem is that premium tiers are systematically over-promised.**

### Hypothesis Testing: Where Are the Drivers?

| Test | Result |
|---|---|
| H1: Late rate differs by **region** | 0 of 23 regions significant after Bonferroni correction |
| H2: Late rate differs by **shipping mode** | 4 of 4 modes significant with **p < 1e-20** |

The geographic dimension is essentially homogeneous. The audit's primary lever is the **shipping mode** — specifically, the SLA promises attached to First Class and Second Class.

### SARIMA Forecast Quality

| Metric | Value |
|---|---|
| Model | SARIMA(1,1,1)×(1,1,1,7) |
| MAE (90-day holdout) | 0.75 orders/day |
| MAPE | **1.09%** |
| 90-day forward forecast | 6,215 total orders |

The series is near-stationary during stable periods, so the forecast is **tight and reliable** for capacity planning.

### SPC Findings

- **Global p-chart:** 1 OOC week of 131 — the dataset is broadly stable
- **Mode-level p-charts:** First Class shows 2 OOC weeks; Same Day shows 5 OOC weeks. The chronic underperformers surface only when you stratify by mode.

---

## Methodology notes

**The brief vs. the data.** The brief asks for Routes, Vehicles, Fuel_Logs, monthly seasonality, and weekly trends. The DataCo dataset is a marketplace dataset, so I made these substitutions and document them clearly in the notebook and schema:

| Brief asks for | We use | Rationale |
|---|---|---|
| Vehicles table | `shipping_modes` table (Standard/First/Second/Same Day) | Operationally-equivalent service tiers, each with its own SLA and OEE profile |
| Routes table | `routes` table (origin-state → destination-state pairs) | Real lane data derived from customer and order locations |
| Fuel_Logs | OEE Performance metric (scheduled_days / actual_days) | Captures the same "energy efficiency" idea without fabrication |
| Monthly seasonality | Documented as **absent** in the data | DoW range 169.9–172.0, monthly range 168.2–174.1, both within one std. SARIMA fits cleanly without it. |
| Weekly trends | Weekly seasonal component s=7 in SARIMA | Detected weak weekly structure; included for completeness |

**This is itself an audit finding.** Telling the operator their volume isn't a forecasting problem (it's near-stationary) and their late-delivery problem isn't a regional problem (it's a product-design problem) is more valuable than fitting elaborate models to noise.

**Recommended actions for the CFO:**

1. **Re-price First Class to a 2-day SLA.** Truthful pricing eliminates the chronic-late perception.
2. **Re-engineer Second Class operations** to actually hit its 2-day SLA (currently 4 days).
3. **Maintain Same Day** — its 0-day SLA is achievable per the data.
4. **Protect Standard Class** as the operational baseline (60% of volume, 53% OEE).
