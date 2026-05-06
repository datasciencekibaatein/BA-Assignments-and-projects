-- =====================================================================
-- Question 1 — DuPont Decomposition of Microsoft's ROE
-- Dataset: Financial Statements of Major Companies (2009-2023)
-- =====================================================================
--
-- Business context:
--   The DuPont identity decomposes ROE into three drivers:
--     ROE = Net Profit Margin × Asset Turnover × Financial Leverage
--          (NI / Revenue) × (Revenue / Assets) × (Assets / Equity)
--
--   This shows WHY a company achieves its ROE — is it through fat
--   margins (operational excellence), efficient asset use (capital
--   discipline), or aggressive leverage (financial risk-taking)?
--
-- Data note:
--   Total Assets is not in the dataset directly, but is mathematically
--   recoverable from the existing ROA column:
--     ROA = Net Income / Total Assets
--     => Total Assets = Net Income / (ROA / 100)
-- =====================================================================


-- ---------------------------------------------------------------------
-- DuPont decomposition for Microsoft (2023, latest year)
-- ---------------------------------------------------------------------
SELECT
    Year,
    Revenue,
    "Net Income",
    "Share Holder Equity"                         AS equity,
    "Net Income" / ("ROA" / 100)                  AS total_assets_derived,
    -- Three DuPont components
    ROUND( ("Net Income" / Revenue) * 100, 2 )    AS net_profit_margin_pct,
    ROUND( Revenue / ("Net Income" / ("ROA"/100)), 4 ) AS asset_turnover,
    ROUND( ("Net Income" / ("ROA"/100)) / "Share Holder Equity", 4 ) AS financial_leverage,
    -- Verify against reported ROE
    ROUND(
        ("Net Income" / Revenue) *
        (Revenue / ("Net Income" / ("ROA"/100))) *
        (("Net Income" / ("ROA"/100)) / "Share Holder Equity") * 100,
        2
    ) AS computed_roe,
    "ROE" AS reported_roe
FROM financial_statements
WHERE TRIM(Company) = 'MSFT'
  AND Year = 2023;


-- ---------------------------------------------------------------------
-- DuPont trend for Microsoft over the last 5 years (2019-2023)
-- Reveals which component is the primary driver and how it shifts
-- ---------------------------------------------------------------------
SELECT
    Year,
    ROUND( ("Net Income" / Revenue) * 100, 2 )    AS npm_pct,
    ROUND( Revenue / ("Net Income" / ("ROA"/100)), 4 ) AS asset_turnover,
    ROUND( ("Net Income" / ("ROA"/100)) / "Share Holder Equity", 4 ) AS financial_leverage,
    ROUND( "ROE", 2 )                             AS roe_pct
FROM financial_statements
WHERE TRIM(Company) = 'MSFT'
  AND Year BETWEEN 2019 AND 2023
ORDER BY Year;


-- =====================================================================
-- RESULTS (verified)
-- =====================================================================
-- Year | NPM    | Asset Turnover | Financial Leverage | ROE
-- 2019 | 31.18% | 0.439          | 2.800              | 38.35%
-- 2020 | 30.96% | 0.475          | 2.547              | 37.43%
-- 2021 | 36.45% | 0.504          | 2.351              | 43.15%
-- 2022 | 36.69% | 0.543          | 2.191              | 43.68%
-- 2023 | 34.15% | 0.514          | 1.998              | 35.09%
--
-- INTERPRETATION:
--   - NPM is the PRIMARY DRIVER. Microsoft's 34% margin is exceptional
--     for any industry — far above S&P 500 median (~10%). This reflects
--     SaaS economics (zero marginal cost, high gross margins).
--   - Asset Turnover is structurally low (~0.5) — Microsoft holds large
--     cash and investment balances, which dilutes the ratio.
--   - Financial Leverage has DECLINED from 2.8 to 2.0 over 5 years,
--     reducing ROE despite stable margins. Microsoft is deleveraging.
-- =====================================================================
