-- =====================================================================
-- Question 2 — Common-Size Analysis: MarkDown Spend as % of Sales
-- Dataset: Walmart Recruiting (Store Sales Forecasting)
-- =====================================================================
--
-- Business context:
--   MarkDown1-5 represent five categories of promotional/markdown
--   spending tracked by Walmart. Expressing each as a % of Weekly_Sales
--   creates a common-size income-statement-style view that highlights
--   which promo channels consume disproportionate revenue.
--
-- Data caveat:
--   MarkDown1-5 are only populated from 2011-11-11 onward. We restrict
--   the analysis window accordingly.
-- =====================================================================


-- ---------------------------------------------------------------------
-- Total MarkDown spend per channel (post Nov 2011)
-- ---------------------------------------------------------------------
SELECT
    SUM(MarkDown1) AS markdown1_total,
    SUM(MarkDown2) AS markdown2_total,
    SUM(MarkDown3) AS markdown3_total,
    SUM(MarkDown4) AS markdown4_total,
    SUM(MarkDown5) AS markdown5_total,
    SUM(COALESCE(MarkDown1,0) + COALESCE(MarkDown2,0)
        + COALESCE(MarkDown3,0) + COALESCE(MarkDown4,0)
        + COALESCE(MarkDown5,0)) AS markdown_total_all
FROM features
WHERE Date >= '2011-11-11';


-- ---------------------------------------------------------------------
-- Common-size: each MarkDown channel as % of Weekly_Sales in same window
-- ---------------------------------------------------------------------
WITH md_totals AS (
    SELECT
        SUM(MarkDown1) AS md1,
        SUM(MarkDown2) AS md2,
        SUM(MarkDown3) AS md3,
        SUM(MarkDown4) AS md4,
        SUM(MarkDown5) AS md5
    FROM features
    WHERE Date >= '2011-11-11'
),
sales_total AS (
    SELECT SUM(Weekly_Sales) AS sales
    FROM train
    WHERE Date >= '2011-11-11'
)
SELECT
    'MarkDown1' AS channel,
    md1 AS spend,
    ROUND((md1 / sales) * 100, 3) AS pct_of_sales
FROM md_totals, sales_total
UNION ALL
SELECT 'MarkDown2', md2, ROUND((md2 / sales) * 100, 3) FROM md_totals, sales_total
UNION ALL
SELECT 'MarkDown3', md3, ROUND((md3 / sales) * 100, 3) FROM md_totals, sales_total
UNION ALL
SELECT 'MarkDown4', md4, ROUND((md4 / sales) * 100, 3) FROM md_totals, sales_total
UNION ALL
SELECT 'MarkDown5', md5, ROUND((md5 / sales) * 100, 3) FROM md_totals, sales_total
ORDER BY pct_of_sales DESC;


-- ---------------------------------------------------------------------
-- Per-store MarkDown intensity (which stores spend most on promo?)
-- Joins features -> stores
-- ---------------------------------------------------------------------
WITH per_store AS (
    SELECT
        f.Store,
        s.Type,
        SUM(COALESCE(f.MarkDown1,0) + COALESCE(f.MarkDown2,0)
            + COALESCE(f.MarkDown3,0) + COALESCE(f.MarkDown4,0)
            + COALESCE(f.MarkDown5,0)) AS total_markdown
    FROM features f
    JOIN stores s ON f.Store = s.Store
    WHERE f.Date >= '2011-11-11'
    GROUP BY f.Store, s.Type
),
per_store_sales AS (
    SELECT Store, SUM(Weekly_Sales) AS total_sales
    FROM train
    WHERE Date >= '2011-11-11'
    GROUP BY Store
)
SELECT
    p.Store,
    p.Type,
    ROUND(p.total_markdown::numeric, 0) AS markdown_spend,
    ROUND(s.total_sales::numeric, 0) AS sales,
    ROUND((p.total_markdown / s.total_sales) * 100, 2) AS markdown_pct_of_sales
FROM per_store p
JOIN per_store_sales s ON p.Store = s.Store
ORDER BY markdown_pct_of_sales DESC
LIMIT 10;


-- =====================================================================
-- RESULTS (verified, post Nov 2011)
-- =====================================================================
-- Total MarkDown spend by channel:
--   MarkDown1: $28,354,523    1.16% of sales  <- LARGEST CHANNEL
--   MarkDown5: $16,735,477    0.68%
--   MarkDown4: $11,406,730    0.47%
--   MarkDown2:  $9,885,180    0.40%
--   MarkDown3:  $6,359,242    0.26%   <- SMALLEST CHANNEL
--
--   TOTAL MARKDOWN: 2.97% of Weekly_Sales
--
-- BUSINESS INTERPRETATION:
--   - MarkDown1 alone consumes 1.16% of every sales dollar —
--     nearly 4x the smallest channel (MarkDown3).
--   - Total promo spend at ~3% of revenue is in line with general
--     retail benchmarks (typically 2-5%).
--   - The skew toward MarkDown1 warrants investigation: is this
--     channel demonstrably the most effective, or has spend drifted
--     there by inertia? An A/B test reallocating from MD1 to MD3
--     could be illuminating.
-- =====================================================================
