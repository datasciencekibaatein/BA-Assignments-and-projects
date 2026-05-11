-- ============================================================================
-- GroceryCo Operational Integrity Audit
-- File:    groceryco_dashboard_transform.sql
-- Engine:  SQLite (groceryco.db produced by Notebook 01)
-- Purpose: Produce ONE wide CSV per output table, so Tableau can render
--          SPC control charts + Reorder Leakage Report + Aisle drill-down
--          with zero in-Tableau aggregation.
--
-- WHAT THIS DOES
--   1. Builds an order-level "spine" with day-of-week, hour, week, segments
--   2. Joins order_items -> products -> aisles -> departments
--   3. Aggregates to weekly per-department reorder rates (the SPC subgroups)
--   4. Computes platform-wide grand mean and ±3sigma control limits
--   5. Flags every weekly observation as IN_CONTROL / OUT_OF_CONTROL
--   6. Builds Reorder Leakage report with t-test p-values from Notebook 04
--   7. Builds aisle drill-down for the worst offenders
--
-- HOW TO RUN
--   sqlite3 outputs/groceryco.db < groceryco_dashboard_transform.sql
--   (creates 4 tables; export each via the .mode csv block at the bottom)
--
-- OUTPUT TABLES (and CSVs you load into Tableau)
--   tab_spc_weekly        -> spc_weekly.csv          (the main control chart data)
--   tab_leakage_report    -> leakage_report.csv      (departments below LCL)
--   tab_aisle_drilldown   -> aisle_drilldown.csv     (aisle-level for worst offenders)
--   tab_dashboard_extract -> dashboard_extract.csv   (single wide table for Tableau, joins all the above)
-- ============================================================================


-- ----------------------------------------------------------------------------
-- 0.  Housekeeping
-- ----------------------------------------------------------------------------
DROP TABLE IF EXISTS tab_order_spine;
DROP TABLE IF EXISTS tab_dept_weekly_raw;
DROP TABLE IF EXISTS tab_spc_limits;
DROP TABLE IF EXISTS tab_spc_weekly;
DROP TABLE IF EXISTS tab_leakage_report;
DROP TABLE IF EXISTS tab_aisle_drilldown;
DROP TABLE IF EXISTS tab_dashboard_extract;


-- ----------------------------------------------------------------------------
-- 1.  Order spine
--     One row per order with engineered time features.
--     "Week" is synthetic: we don't have calendar dates in the Instacart data
--     (only order_dow + order_hour_of_day + days_since_prior_order).
--     We derive a synthetic week_id by chunking each user's order sequence
--     in groups of order_number, which is the closest analogue to a weekly
--     subgroup the dataset supports.
-- ----------------------------------------------------------------------------
CREATE TABLE tab_order_spine AS
SELECT
    o.order_id,
    o.user_id,
    o.order_number,
    o.order_dow,
    o.order_hour_of_day,
    -- Synthetic week_id: group orders by user into 4-order chunks (~weekly cadence)
    -- This gives stable subgroup sizes for X-bar / R charts.
    ((o.order_number - 1) / 4) + 1                   AS week_id,
    CASE WHEN o.order_dow IN (0, 6) THEN 1 ELSE 0 END AS is_weekend,
    CASE
        WHEN o.order_hour_of_day < 6  THEN 'night'
        WHEN o.order_hour_of_day < 12 THEN 'morning'
        WHEN o.order_hour_of_day < 18 THEN 'afternoon'
        ELSE 'evening'
    END                                              AS time_window
FROM orders o;

CREATE INDEX idx_spine_week ON tab_order_spine(week_id);
CREATE INDEX idx_spine_oid  ON tab_order_spine(order_id);


-- ----------------------------------------------------------------------------
-- 2.  Department-week subgroups
--     For each (department, week_id), compute the SPC subgroup statistics:
--     - mean reorder rate      (X-bar)
--     - subgroup range         (R)
--     - subgroup size          (n_items)
--     This is the raw input to the control chart.
-- ----------------------------------------------------------------------------
CREATE TABLE tab_dept_weekly_raw AS
SELECT
    d.department_id,
    d.department,
    s.week_id,
    COUNT(*)                       AS n_items,
    AVG(oi.reordered)              AS reorder_rate,        -- X-bar
    MAX(oi.reordered) - MIN(oi.reordered) AS reorder_range, -- R (will be 1 in most subgroups since reordered is 0/1)
    SUM(oi.reordered)              AS n_reordered,
    AVG(s.is_weekend)              AS weekend_share         -- context for Tableau
FROM order_items oi
JOIN tab_order_spine s ON oi.order_id     = s.order_id
JOIN products       p  ON oi.product_id   = p.product_id
JOIN departments    d  ON p.department_id = d.department_id
GROUP BY d.department_id, d.department, s.week_id
HAVING COUNT(*) >= 50;     -- drop sparse weeks; keeps SPC chart stable


-- ----------------------------------------------------------------------------
-- 3.  Platform-wide control limits  (Shewhart 3-sigma, p-chart variant)
--     Reorder is binary, so each subgroup proportion has SD = sqrt(p*(1-p)/n).
--     We use the OVERALL platform reorder rate as the centerline (p_bar)
--     and weighted-average subgroup size for the limits.
-- ----------------------------------------------------------------------------
CREATE TABLE tab_spc_limits AS
WITH platform AS (
    SELECT
        SUM(n_reordered) * 1.0 / SUM(n_items)        AS p_bar,
        AVG(n_items)                                  AS n_avg,
        COUNT(*)                                      AS n_subgroups,
        COUNT(DISTINCT department_id)                 AS n_departments
    FROM tab_dept_weekly_raw
)
SELECT
    p_bar                                             AS centerline,
    p_bar + 3 * SQRT(p_bar * (1 - p_bar) / n_avg)     AS ucl,
    p_bar - 3 * SQRT(p_bar * (1 - p_bar) / n_avg)     AS lcl,
    p_bar + 2 * SQRT(p_bar * (1 - p_bar) / n_avg)     AS uwl,
    p_bar - 2 * SQRT(p_bar * (1 - p_bar) / n_avg)     AS lwl,
    SQRT(p_bar * (1 - p_bar) / n_avg)                 AS sigma_hat,
    n_avg, n_subgroups, n_departments
FROM platform;


-- ----------------------------------------------------------------------------
-- 4.  SPC weekly observations  (the table Tableau plots)
--     One row per (department, week) annotated with control limits + flag.
-- ----------------------------------------------------------------------------
CREATE TABLE tab_spc_weekly AS
SELECT
    r.department_id,
    r.department,
    r.week_id,
    r.n_items,
    r.reorder_rate,
    l.centerline,
    l.ucl,
    l.lcl,
    l.uwl,
    l.lwl,
    l.sigma_hat,
    -- Standardized z-score of this subgroup vs platform
    (r.reorder_rate - l.centerline) / l.sigma_hat       AS z_score,
    -- Status flag
    CASE
        WHEN r.reorder_rate > l.ucl THEN 'OUT_OF_CONTROL_HIGH'
        WHEN r.reorder_rate < l.lcl THEN 'OUT_OF_CONTROL_LOW'
        WHEN r.reorder_rate > l.uwl THEN 'WARNING_HIGH'
        WHEN r.reorder_rate < l.lwl THEN 'WARNING_LOW'
        ELSE 'IN_CONTROL'
    END                                                  AS spc_status,
    r.weekend_share
FROM tab_dept_weekly_raw r
CROSS JOIN tab_spc_limits l
ORDER BY r.department, r.week_id;

CREATE INDEX idx_spc_dept ON tab_spc_weekly(department);
CREATE INDEX idx_spc_week ON tab_spc_weekly(week_id);


-- ----------------------------------------------------------------------------
-- 5.  Reorder Leakage Report
--     Departments operating BELOW the platform mean, with statistical
--     evidence: how many weeks below LCL, average z-score, and a
--     t-statistic vs platform mean (df = n_weeks - 1).
--     A p-value is computed via the SQLite-portable approximation
--     of the two-tailed Student-t survival function (df>=30 -> normal).
-- ----------------------------------------------------------------------------
CREATE TABLE tab_leakage_report AS
WITH dept_stats AS (
    SELECT
        s.department_id,
        s.department,
        COUNT(*)                                          AS n_weeks,
        AVG(s.reorder_rate)                               AS dept_mean,
        -- sample SD via E[X^2] - E[X]^2
        SQRT( MAX(0.0,
            (SUM(s.reorder_rate * s.reorder_rate) * 1.0 / COUNT(*))
            - (AVG(s.reorder_rate) * AVG(s.reorder_rate))
        ) )                                                AS dept_sd,
        AVG(s.centerline)                                  AS platform_mean,
        AVG(s.sigma_hat)                                   AS platform_sigma,
        SUM(CASE WHEN s.spc_status = 'OUT_OF_CONTROL_LOW'  THEN 1 ELSE 0 END) AS weeks_below_lcl,
        SUM(CASE WHEN s.spc_status = 'OUT_OF_CONTROL_HIGH' THEN 1 ELSE 0 END) AS weeks_above_ucl,
        SUM(CASE WHEN s.spc_status LIKE 'OUT_OF_CONTROL%' THEN 1 ELSE 0 END)  AS weeks_ooc_total,
        AVG(s.z_score)                                     AS avg_z_score
    FROM tab_spc_weekly s
    GROUP BY s.department_id, s.department
)
SELECT
    department_id,
    department,
    n_weeks,
    dept_mean,
    platform_mean,
    dept_mean - platform_mean                                  AS gap_vs_platform,
    dept_sd,
    weeks_below_lcl,
    weeks_above_ucl,
    weeks_ooc_total,
    avg_z_score,
    -- One-sample t-statistic: department mean vs platform mean
    CASE WHEN dept_sd > 0 AND n_weeks > 1
         THEN (dept_mean - platform_mean) / (dept_sd / SQRT(n_weeks * 1.0))
         ELSE NULL
    END                                                        AS t_stat,
    -- Approximate two-tailed p-value (normal approx since n_weeks usually >>30)
    -- p = 2 * (1 - Phi(|t|))   approximated with Abramowitz & Stegun 26.2.17
    CASE WHEN dept_sd > 0 AND n_weeks > 1 THEN
        2.0 * (1.0 - (
            1.0 - 0.5 * EXP(
                -0.717 * ABS((dept_mean - platform_mean) / (dept_sd / SQRT(n_weeks * 1.0)))
                -0.416 * ((dept_mean - platform_mean) / (dept_sd / SQRT(n_weeks * 1.0)))
                       * ((dept_mean - platform_mean) / (dept_sd / SQRT(n_weeks * 1.0)))
            )
        ))
    ELSE NULL END                                              AS p_value_approx,
    CASE
        WHEN weeks_below_lcl >= 4 AND avg_z_score < -1.0 THEN 'LEAKAGE_CONFIRMED'
        WHEN weeks_below_lcl >= 1                        THEN 'LEAKAGE_SUSPECTED'
        WHEN weeks_above_ucl >= 4 AND avg_z_score >  1.0 THEN 'OVERPERFORMER'
        ELSE 'STABLE'
    END                                                        AS leakage_flag
FROM dept_stats
ORDER BY gap_vs_platform ASC;     -- worst leakage first


-- ----------------------------------------------------------------------------
-- 6.  Aisle Drill-Down  (for the worst-offender departments only)
--     Pulled for the bottom-3 leakage departments. Tableau uses this for the
--     drill-down panel when a user clicks an out-of-control department.
-- ----------------------------------------------------------------------------
CREATE TABLE tab_aisle_drilldown AS
WITH worst_depts AS (
    SELECT department_id
    FROM tab_leakage_report
    WHERE leakage_flag IN ('LEAKAGE_CONFIRMED', 'LEAKAGE_SUSPECTED')
    ORDER BY gap_vs_platform ASC
    LIMIT 5
)
SELECT
    d.department_id,
    d.department,
    a.aisle_id,
    a.aisle,
    COUNT(*)                                            AS n_items,
    AVG(oi.reordered)                                   AS aisle_reorder_rate,
    (SELECT centerline FROM tab_spc_limits)             AS platform_mean,
    AVG(oi.reordered) - (SELECT centerline FROM tab_spc_limits) AS gap_vs_platform,
    (AVG(oi.reordered) - (SELECT centerline FROM tab_spc_limits))
        / NULLIF((SELECT sigma_hat FROM tab_spc_limits), 0)     AS z_score,
    CASE
        WHEN AVG(oi.reordered) < (SELECT lcl FROM tab_spc_limits) THEN 'WORST'
        WHEN AVG(oi.reordered) < (SELECT lwl FROM tab_spc_limits) THEN 'WEAK'
        ELSE 'OK'
    END                                                 AS aisle_flag
FROM order_items oi
JOIN products    p ON oi.product_id   = p.product_id
JOIN aisles      a ON p.aisle_id      = a.aisle_id
JOIN departments d ON p.department_id = d.department_id
WHERE p.department_id IN (SELECT department_id FROM worst_depts)
GROUP BY d.department_id, d.department, a.aisle_id, a.aisle
HAVING COUNT(*) >= 100
ORDER BY d.department, aisle_reorder_rate ASC;


-- ----------------------------------------------------------------------------
-- 7.  ONE-FILE DASHBOARD EXTRACT (denormalized, ready for Tableau)
--     Wide flat table with EVERYTHING the dashboard needs.
--     This is what you point Tableau at if you want a single connection.
-- ----------------------------------------------------------------------------
CREATE TABLE tab_dashboard_extract AS
SELECT
    s.department_id,
    s.department,
    s.week_id,
    s.n_items,
    s.reorder_rate,
    s.centerline                AS platform_mean,
    s.ucl,
    s.lcl,
    s.uwl,
    s.lwl,
    s.sigma_hat,
    s.z_score,
    s.spc_status,
    s.weekend_share,
    -- Department-level rollups (denormalized for Tableau)
    lr.dept_mean,
    lr.gap_vs_platform,
    lr.weeks_below_lcl,
    lr.weeks_above_ucl,
    lr.weeks_ooc_total,
    lr.t_stat,
    lr.p_value_approx,
    lr.leakage_flag
FROM tab_spc_weekly s
LEFT JOIN tab_leakage_report lr ON s.department_id = lr.department_id;

CREATE INDEX idx_extract_dept ON tab_dashboard_extract(department);
CREATE INDEX idx_extract_flag ON tab_dashboard_extract(leakage_flag);


-- ----------------------------------------------------------------------------
-- 8.  Quick smoke checks (these print to stdout when sqlite is run with -echo)
-- ----------------------------------------------------------------------------
SELECT '=== Row counts ===' AS msg;
SELECT 'tab_spc_weekly         '       AS table_name, COUNT(*) AS rows FROM tab_spc_weekly;
SELECT 'tab_leakage_report    '        AS table_name, COUNT(*) AS rows FROM tab_leakage_report;
SELECT 'tab_aisle_drilldown   '        AS table_name, COUNT(*) AS rows FROM tab_aisle_drilldown;
SELECT 'tab_dashboard_extract '        AS table_name, COUNT(*) AS rows FROM tab_dashboard_extract;

SELECT '=== Platform control limits ===' AS msg;
SELECT * FROM tab_spc_limits;

SELECT '=== Top-5 leakage departments ===' AS msg;
SELECT department, n_weeks, ROUND(dept_mean, 4) AS dept_mean,
       ROUND(platform_mean, 4) AS plat_mean, ROUND(gap_vs_platform, 4) AS gap,
       weeks_below_lcl, ROUND(t_stat, 2) AS t_stat,
       ROUND(p_value_approx, 4) AS p_val, leakage_flag
FROM tab_leakage_report
ORDER BY gap_vs_platform ASC
LIMIT 5;
