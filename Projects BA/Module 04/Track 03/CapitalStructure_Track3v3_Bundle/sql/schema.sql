-- ============================================================================
-- Capital Structure Audit - SQLite Schema
-- For Track 3: Risk & Financial track
-- 3 base tables + 5 analytical views
-- ============================================================================

DROP TABLE IF EXISTS leverage_scenarios;
DROP TABLE IF EXISTS vol_regimes;
DROP TABLE IF EXISTS brent_prices;

-- ---------- BASE TABLES ----------

CREATE TABLE brent_prices (
    price_date    TEXT PRIMARY KEY,        -- ISO date
    price_usd     REAL,                    -- Brent spot $/bbl
    log_return    REAL,                    -- log(P_t / P_{t-1})
    cond_vol_ann  REAL                     -- GARCH conditional vol (annualized %)
);

CREATE TABLE vol_regimes (
    regime_id     INTEGER PRIMARY KEY,
    regime_label  TEXT,
    vol_lower     REAL,                    -- annualized %
    vol_upper     REAL,
    description   TEXT
);

CREATE TABLE leverage_scenarios (
    scenario_id   INTEGER PRIMARY KEY,
    dv_ratio      REAL,                    -- D/V
    de_ratio      REAL,                    -- D/E
    debt_amount   REAL,                    -- $
    tax_shield    REAL,                    -- $
    v_levered     REAL,                    -- $
    beta_levered  REAL,
    ke_pct        REAL,                    -- cost of equity
    kd_pct        REAL,                    -- pre-tax cost of debt
    wacc_pct      REAL
);

CREATE INDEX idx_brent_date ON brent_prices(price_date);
CREATE INDEX idx_lev_dv     ON leverage_scenarios(dv_ratio);


-- ---------- ANALYTICAL VIEWS ----------

DROP VIEW IF EXISTS v_yearly_brent_summary;
DROP VIEW IF EXISTS v_decade_vol_clusters;
DROP VIEW IF EXISTS v_vol_regime_freq;
DROP VIEW IF EXISTS v_optimal_leverage;
DROP VIEW IF EXISTS v_extreme_returns;


-- 1. Yearly summary of Brent prices and volatility
CREATE VIEW v_yearly_brent_summary AS
SELECT
    SUBSTR(price_date, 1, 4) AS year,
    COUNT(*)                  AS n_obs,
    MIN(price_usd)            AS price_min,
    MAX(price_usd)            AS price_max,
    AVG(price_usd)            AS price_avg,
    AVG(log_return)*252       AS annualized_return,
    AVG(cond_vol_ann)         AS avg_cond_vol
FROM brent_prices
WHERE log_return IS NOT NULL
GROUP BY SUBSTR(price_date, 1, 4)
ORDER BY year;


-- 2. Decade-level volatility clustering
CREATE VIEW v_decade_vol_clusters AS
SELECT
    SUBSTR(price_date, 1, 3) || '0s' AS decade,
    COUNT(*)                          AS n_obs,
    AVG(cond_vol_ann)                 AS avg_vol,
    MAX(cond_vol_ann)                 AS peak_vol
FROM brent_prices
WHERE cond_vol_ann IS NOT NULL
GROUP BY SUBSTR(price_date, 1, 3)
ORDER BY decade;


-- 3. Vol regime frequency (how much time in each regime)
CREATE VIEW v_vol_regime_freq AS
SELECT
    r.regime_label,
    r.vol_lower,
    r.vol_upper,
    COUNT(b.price_date) AS n_days,
    100.0 * COUNT(b.price_date) / (SELECT COUNT(*) FROM brent_prices WHERE cond_vol_ann IS NOT NULL) AS pct_of_history
FROM vol_regimes r
LEFT JOIN brent_prices b ON b.cond_vol_ann >= r.vol_lower AND b.cond_vol_ann < r.vol_upper
GROUP BY r.regime_id, r.regime_label, r.vol_lower, r.vol_upper
ORDER BY r.regime_id;


-- 4. Optimal leverage (lowest WACC point)
CREATE VIEW v_optimal_leverage AS
SELECT *
FROM leverage_scenarios
WHERE wacc_pct = (SELECT MIN(wacc_pct) FROM leverage_scenarios);


-- 5. Extreme returns (top 20 single-day moves) - for tail-risk illustration
CREATE VIEW v_extreme_returns AS
SELECT
    price_date,
    price_usd,
    log_return,
    cond_vol_ann,
    CASE WHEN log_return < 0 THEN 'CRASH' ELSE 'SPIKE' END AS event_type
FROM brent_prices
WHERE ABS(log_return) > 0.10
ORDER BY ABS(log_return) DESC
LIMIT 20;
