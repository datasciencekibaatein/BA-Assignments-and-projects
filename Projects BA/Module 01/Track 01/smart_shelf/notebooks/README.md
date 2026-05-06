# Smart-Shelf — Jupyter Notebooks

7 self-contained notebooks. Run in order 01 → 07.

## Folder layout (required)

Place the notebooks anywhere inside `smart_shelf/` (recommended: a `notebooks/` subfolder).
The path-resolution cell at the top of every notebook auto-detects the project root.

```
Track 01/
├── dataset/                          ← Olist CSVs (8 olist_*.csv + 1 product_category_*.csv)
└── smart_shelf/
    └── notebooks/                    ← put the .ipynb files here
        ├── 01_data_architecture.ipynb
        ├── 02_otif_cycle_diagnostic.ipynb
        ├── 03_delay_churn_heatmap.ipynb
        ├── 04_automated_margin_report.ipynb
        ├── 05_build_bullwhip_xlsx.ipynb
        ├── 06_build_supply_chain_xlsx.ipynb
        └── 07_build_executive_report.ipynb
```

The `data/`, `outputs/`, and `figures/` folders are created automatically when notebook 01 runs.

## How to run

1. Open Jupyter / VS Code / Cursor.
2. Open `01_data_architecture.ipynb` first.
3. Run the **Setup — auto-resolving paths** cell. It will print all the resolved paths.
   If `Dataset folder not found` errors out, your `dataset/` folder is in the wrong place.
4. Run all remaining cells top-to-bottom.
5. Repeat for notebooks 02-07.

## Dependencies

```bash
pip install pandas numpy seaborn matplotlib openpyxl reportlab pyarrow
```

## What each notebook produces

| Notebook | Task | Output |
|---|---|---|
| 01 | Task 1 | `data/master_orders.parquet` (112,650 rows × 43 cols) |
| 02 | Task 2 | OTIF + Cycle Time CSVs, `diagnosis.txt` |
| 03 | Task 4 | `figures/delay_churn_heatmap.png` |
| 04 | Deliverable 1 | `margin_leak_report.csv`, `top50_margin_leaks.csv` + 2 figures |
| 05 | Task 3 | `Bullwhip_Simulator.xlsx` |
| 06 | Deliverable 2 | `Supply_Chain_Simulator.xlsx` |
| 07 | Final report | `Smart_Shelf_Executive_Report.pdf` (9 pages) |

## Notes

- Notebook 01 must run **before** any other notebook (the others read its parquet output).
- Notebook 07 should run **last** (it pulls figures from notebooks 03 & 04).
- Notebooks 02, 03, 04 are independent of each other once 01 is done.
