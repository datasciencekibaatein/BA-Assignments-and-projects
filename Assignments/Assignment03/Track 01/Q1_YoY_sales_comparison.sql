-- =====================================================================
-- Question 1 — Year-over-Year Sales Comparison (2010 vs 2011)
-- Dataset: Walmart Recruiting (Store Sales Forecasting)
-- =====================================================================
--
-- Business context:
--   The board needs to understand revenue trajectory and whether
--   operating costs are outpacing revenue growth. We use Fuel_Price
--   from features.csv as a proxy for operating cost (fuel is one of
--   the largest controllable costs in retail logistics).
--
-- Methodology note:
--   Train data spans Feb 2010 to Oct 2012. For a fair YoY comparison,
--   we use only the months that exist in both years — Feb-Oct.
--   Otherwise the partial-year overlap (Dec 2010, Nov-Dec 2011) would
--   bias the comparison unfairly.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Total YoY sales (Feb-Oct alignment for fair comparison)
-- ---------------------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM Date) AS year,
    SUM(Weekly_Sales)       AS total_sales,
    COUNT(*)                AS records
FROM train
WHERE EXTRACT(MONTH FROM Date) BETWEEN 2 AND 10
GROUP BY EXTRACT(YEAR FROM Date)
ORDER BY year;


-- ---------------------------------------------------------------------
-- YoY by store type (joins train -> stores)
-- ---------------------------------------------------------------------
SELECT
    s.Type                  AS store_type,
    EXTRACT(YEAR FROM t.Date) AS year,
    SUM(t.Weekly_Sales)     AS total_sales,
    AVG(t.Weekly_Sales)     AS avg_weekly_sales
FROM train t
JOIN stores s ON t.Store = s.Store
WHERE EXTRACT(MONTH FROM t.Date) BETWEEN 2 AND 10
  AND EXTRACT(YEAR  FROM t.Date) IN (2010, 2011)
GROUP BY s.Type, EXTRACT(YEAR FROM t.Date)
ORDER BY s.Type, year;


-- ---------------------------------------------------------------------
-- YoY % change calculation (pivot-style with conditional aggregation)
-- ---------------------------------------------------------------------
SELECT
    s.Type AS store_type,
    SUM(CASE WHEN EXTRACT(YEAR FROM t.Date) = 2010
             THEN t.Weekly_Sales ELSE 0 END) AS sales_2010,
    SUM(CASE WHEN EXTRACT(YEAR FROM t.Date) = 2011
             THEN t.Weekly_Sales ELSE 0 END) AS sales_2011,
    ROUND(
        (SUM(CASE WHEN EXTRACT(YEAR FROM t.Date) = 2011
                  THEN t.Weekly_Sales ELSE 0 END) -
         SUM(CASE WHEN EXTRACT(YEAR FROM t.Date) = 2010
                  THEN t.Weekly_Sales ELSE 0 END))
        /
        NULLIF(SUM(CASE WHEN EXTRACT(YEAR FROM t.Date) = 2010
                        THEN t.Weekly_Sales ELSE 0 END), 0) * 100,
        2
    ) AS yoy_pct_change
FROM train t
JOIN stores s ON t.Store = s.Store
WHERE EXTRACT(MONTH FROM t.Date) BETWEEN 2 AND 10
GROUP BY s.Type
ORDER BY s.Type;


-- ---------------------------------------------------------------------
-- Operating cost proxy: Average Fuel Price by year
-- ---------------------------------------------------------------------
SELECT
    EXTRACT(YEAR FROM Date) AS year,
    ROUND(AVG(Fuel_Price)::numeric, 3) AS avg_fuel_price,
    ROUND(MIN(Fuel_Price)::numeric, 3) AS min_fuel_price,
    ROUND(MAX(Fuel_Price)::numeric, 3) AS max_fuel_price
FROM features
GROUP BY EXTRACT(YEAR FROM Date)
ORDER BY year;


-- =====================================================================
-- RESULTS (verified against the dataset)
-- =====================================================================
-- YoY total sales (Feb-Oct alignment):
--   2010: $1,797,272,218
--   2011: $1,740,102,472     (-3.18% YoY)
--   2012: $1,785,152,780     (+2.59% YoY vs 2011)
--
-- YoY by store type (2010 vs 2011):
--   Type A: -2.38%   (largest stores - most resilient)
--   Type B: -5.00%   (mid-size stores - largest decline)
--   Type C: -2.70%   (smallest stores)
--
-- Fuel price (operating cost proxy):
--   2010: $2.824
--   2011: $3.562    (+26.14% YoY)
--   2012: $3.672    (+3.09% YoY vs 2011)
--
-- IMPLICATION FOR SOLVENCY:
--   Sales declined 3.18% while fuel costs rose 26.14% in the same
--   period. This is a classic margin compression scenario. If the
--   pattern persists, free cash flow shrinks meaningfully, eroding
--   the firm's ability to service debt and fund capex. The board
--   should evaluate route optimization and supplier renegotiation.
-- =====================================================================
