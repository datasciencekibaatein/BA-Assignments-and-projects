-- =====================================================================
-- Question 7 — Asset Turnover Benchmark: MSFT vs GOOG vs AMZN
-- Dataset: Financial Statements of Major Companies (2009-2023)
-- =====================================================================
--
-- Business context:
--   Asset Turnover (Revenue / Total Assets) measures how efficiently
--   a company converts its asset base into revenue. Higher = better
--   capital efficiency.
--
--   We benchmark Microsoft against Google and Amazon — the two other
--   cloud/tech megaplays in the dataset — to assess relative efficiency.
--
-- Data note:
--   GOOG and AMZN data ends in 2022, so we use 2022 as the comparable
--   year for direct cross-company benchmarking.
-- =====================================================================


-- ---------------------------------------------------------------------
-- 2022 Asset Turnover comparison across the three cloud peers
-- ---------------------------------------------------------------------
SELECT
    TRIM(Company) AS company,
    Year,
    Revenue,
    "Net Income" / ("ROA" / 100)              AS total_assets_derived,
    ROUND( Revenue / ("Net Income" / ("ROA"/100)), 4 ) AS asset_turnover,
    ROUND( "Net Profit Margin", 2 )           AS net_profit_margin_pct,
    ROUND( "ROA", 2 )                         AS roa_pct
FROM financial_statements
WHERE TRIM(Company) IN ('MSFT', 'GOOG', 'AMZN')
  AND Year = 2022
ORDER BY asset_turnover DESC;


-- ---------------------------------------------------------------------
-- 10-year asset turnover trend for all three peers (2013-2022)
-- ---------------------------------------------------------------------
SELECT
    TRIM(Company) AS company,
    Year,
    ROUND( Revenue / ("Net Income" / ("ROA"/100)), 4 ) AS asset_turnover
FROM financial_statements
WHERE TRIM(Company) IN ('MSFT', 'GOOG', 'AMZN')
  AND Year BETWEEN 2013 AND 2022
ORDER BY company, Year;


-- =====================================================================
-- RESULTS (verified, 2022)
-- =====================================================================
-- Company | Revenue   | Total Assets | Asset Turnover | NPM     | ROA
-- AMZN    | $513,983M | $462,689M    | 1.111          | -0.53%  | -0.59%
-- GOOG    | $282,836M | $365,264M    | 0.774          | 21.20%  | 16.42%
-- MSFT    | $198,270M | $364,839M    | 0.543          | 36.69%  | 19.94%
--
-- INTERPRETATION:
--   AMZN has the HIGHEST asset turnover (1.11) — every $1 of assets
--   generates $1.11 in revenue. This reflects retail/marketplace
--   economics — high volume, thin margins.
--
--   MSFT has the LOWEST turnover (0.54) but the HIGHEST profit margin
--   (36.7%). It generates ROUGHLY HALF the revenue per dollar of assets
--   compared to AMZN, but converts that revenue to profit at 70x AMZN's
--   margin.
--
--   STRATEGIC TAKEAWAY:
--   Microsoft's "low" asset turnover is NOT inefficiency — it's a
--   capital structure choice. Microsoft holds ~$100B in cash and
--   investments that suppress the ratio. Its true operating asset
--   efficiency (excluding financial assets) is much higher.
--
--   The right ROE-driver mix differs by business model:
--     - AMZN: thin margin × HIGH turnover = volume strategy
--     - MSFT: HIGH margin × moderate turnover = value strategy
--     - GOOG: balanced (moderate × moderate)
--
--   For an SaaS startup pitching Series B, the MSFT model is the
--   one to emulate — investors pay premium multiples for high-margin
--   recurring revenue, not for asset throughput.
-- =====================================================================
