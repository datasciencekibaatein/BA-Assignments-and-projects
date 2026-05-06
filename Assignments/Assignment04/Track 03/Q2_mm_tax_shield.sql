-- =====================================================================
-- Question 2 — Modigliani-Miller Tax Shield Calculation
-- Dataset: Financial Statements of Major Companies (2009-2023)
-- =====================================================================
--
-- Modigliani-Miller Theorem (with corporate taxes):
--   V_levered = V_unlevered + Tax_Shield
--   Tax_Shield = Tax_Rate × Total_Debt
--
-- Business context:
--   The dataset has no "Total Debt" column — we derive it from the
--   Debt/Equity ratio: Debt = D/E_Ratio × Shareholder_Equity
-- =====================================================================


-- ---------------------------------------------------------------------
-- Tax shield value across 15 years for Microsoft
-- ---------------------------------------------------------------------
WITH tax_shield_calc AS (
    SELECT
        Year,
        TRIM(Company) AS company,
        "Share Holder Equity"                                     AS equity,
        "Debt/Equity Ratio"                                       AS de_ratio,
        ROUND(("Debt/Equity Ratio" * "Share Holder Equity")::numeric, 0)
                                                                  AS total_debt,
        ROUND((0.21 * "Debt/Equity Ratio" * "Share Holder Equity")::numeric, 0)
                                                                  AS tax_shield_21pct,
        "Market Cap(in B USD)" * 1000                             AS market_cap_M
    FROM financial_statements
    WHERE TRIM(Company) = 'MSFT'
)
SELECT
    Year,
    equity,
    de_ratio,
    total_debt,
    tax_shield_21pct,
    market_cap_M,
    ROUND((tax_shield_21pct * 100.0 / NULLIF(market_cap_M, 0))::numeric, 3)
        AS tax_shield_as_pct_of_mcap
FROM tax_shield_calc
ORDER BY Year;


-- ---------------------------------------------------------------------
-- Cross-company tax shield comparison (latest year)
-- ---------------------------------------------------------------------
SELECT
    TRIM(Company)                             AS company,
    Year,
    "Debt/Equity Ratio"                       AS de_ratio,
    "Share Holder Equity"                     AS equity,
    ROUND(("Debt/Equity Ratio" * "Share Holder Equity")::numeric, 0)
                                              AS total_debt,
    ROUND((0.21 * "Debt/Equity Ratio" * "Share Holder Equity")::numeric, 0)
                                              AS tax_shield
FROM financial_statements
WHERE Year = 2022
  AND "Debt/Equity Ratio" > 0
ORDER BY tax_shield DESC;


-- =====================================================================
-- RESULTS (verified for MSFT)
-- =====================================================================
-- Year | Equity      | D/E    | Debt       | Tax Shield | % of MCap
-- 2017 | $87,711M    | 0.98   | $86,194M   | $18,101M   | 2.74%
-- 2023 | $206,223M   | 0.23   | $47,246M   | $9,922M    | 0.40%
--
-- KEY INSIGHTS:
--   1. Tax shield value PEAKED in 2017 ($18.1B) when D/E was at maximum.
--   2. Current 2023 tax shield is $9.9B = 0.40% of $2.45T market cap —
--      relatively small because MSFT has been deleveraging.
--   3. The MM theorem says firm value INCREASES by the tax shield amount.
--      For MSFT, every $1 of debt creates $0.21 of value (at 21% tax rate)
--      — but this benefit is offset by financial distress costs at high
--      D/E levels (see Q3 trade-off analysis).
--
-- BUSINESS IMPLICATION:
--   MSFT could have re-leveraged for a $20B+ tax shield, but instead
--   chose to deleverage. The $20B foregone tax benefit reflects MSFT's
--   strategic preference for financial flexibility over leverage gains.
-- =====================================================================
