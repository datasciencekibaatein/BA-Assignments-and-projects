-- ============================================================================
-- groceryco_export_csvs.sql
-- Run AFTER groceryco_dashboard_transform.sql to export 4 Tableau-ready CSVs.
--
-- Usage:
--   sqlite3 outputs/groceryco.db < sql/groceryco_export_csvs.sql
--
-- This produces 4 CSVs in the current directory.
-- Move them to your Tableau project folder and connect.
-- ============================================================================

.headers on
.mode csv

.output spc_weekly.csv
SELECT * FROM tab_spc_weekly;

.output leakage_report.csv
SELECT * FROM tab_leakage_report;

.output aisle_drilldown.csv
SELECT * FROM tab_aisle_drilldown;

.output dashboard_extract.csv
SELECT * FROM tab_dashboard_extract;

.output stdout
SELECT 'Exported: spc_weekly.csv, leakage_report.csv, aisle_drilldown.csv, dashboard_extract.csv' AS done;
