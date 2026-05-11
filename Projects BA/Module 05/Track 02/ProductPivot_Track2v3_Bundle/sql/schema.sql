-- =====================================================================
-- PivotCo Customer Lifecycle Analytics - SQLite Schema
-- =====================================================================
-- Source: IBM Telco Customer Churn (7,043 customers, 21 fields)
-- Purpose: Star schema for SaaS retention/funnel/segmentation analysis
-- =====================================================================

DROP TABLE IF EXISTS fact_customer_state;
DROP TABLE IF EXISTS dim_subscriber;
DROP TABLE IF EXISTS dim_contract;
DROP TABLE IF EXISTS dim_payment;

-- =====================================================================
-- DIMENSIONS
-- =====================================================================

CREATE TABLE dim_subscriber (
    customer_id        TEXT PRIMARY KEY,
    gender             TEXT,
    senior_citizen     INTEGER,
    has_partner        TEXT,
    has_dependents     TEXT
);

CREATE TABLE dim_contract (
    contract_type      TEXT PRIMARY KEY,
    avg_lock_in_months INTEGER,
    commitment_tier    TEXT
);

CREATE TABLE dim_payment (
    payment_method     TEXT PRIMARY KEY,
    is_automatic       INTEGER,
    friction_score     INTEGER  -- 1=lowest friction, 5=highest
);

-- =====================================================================
-- FACT (one row per customer = current snapshot)
-- =====================================================================

CREATE TABLE fact_customer_state (
    customer_id            TEXT PRIMARY KEY,
    tenure_months          INTEGER,
    monthly_charges        REAL,
    total_charges          REAL,                 -- nullable (11 new customers blank)
    contract_type          TEXT,
    payment_method         TEXT,
    paperless_billing      TEXT,
    -- Service / feature flags
    has_phone              TEXT,
    has_multiple_lines     TEXT,
    internet_service       TEXT,                 -- DSL / Fiber optic / No
    has_online_security    TEXT,
    has_online_backup      TEXT,
    has_device_protection  TEXT,
    has_tech_support       TEXT,
    has_streaming_tv       TEXT,
    has_streaming_movies   TEXT,
    -- Derived
    features_adopted       INTEGER,
    tenure_bucket          TEXT,                 -- AAARRR funnel stage
    -- Target
    churn                  TEXT,                 -- Yes/No
    churn_flag             INTEGER,              -- 1/0
    FOREIGN KEY (customer_id)    REFERENCES dim_subscriber(customer_id),
    FOREIGN KEY (contract_type)  REFERENCES dim_contract(contract_type),
    FOREIGN KEY (payment_method) REFERENCES dim_payment(payment_method)
);

CREATE INDEX idx_fact_contract  ON fact_customer_state(contract_type);
CREATE INDEX idx_fact_payment   ON fact_customer_state(payment_method);
CREATE INDEX idx_fact_tenure    ON fact_customer_state(tenure_bucket);
CREATE INDEX idx_fact_churn     ON fact_customer_state(churn_flag);

-- =====================================================================
-- ANALYTICAL VIEWS
-- =====================================================================

-- DEFINE: Funnel by tenure bucket
DROP VIEW IF EXISTS v_funnel_by_tenure;
CREATE VIEW v_funnel_by_tenure AS
SELECT
    tenure_bucket,
    COUNT(*) AS n,
    SUM(churn_flag) AS n_churned,
    AVG(churn_flag * 1.0) AS churn_rate,
    AVG(monthly_charges) AS avg_monthly,
    SUM(monthly_charges) AS total_monthly_revenue
FROM fact_customer_state
GROUP BY tenure_bucket;

-- MEASURE: Churn by contract type (decision tree input)
DROP VIEW IF EXISTS v_churn_by_contract;
CREATE VIEW v_churn_by_contract AS
SELECT
    contract_type,
    COUNT(*) AS n,
    AVG(churn_flag * 1.0) AS churn_rate,
    1.0 / NULLIF(AVG(churn_flag * 1.0), 0) AS expected_lifetime_months,
    AVG(monthly_charges) AS avg_monthly,
    AVG(monthly_charges) * (1.0 / NULLIF(AVG(churn_flag * 1.0), 0)) AS expected_ltv
FROM fact_customer_state
GROUP BY contract_type;

-- ANALYZE: MECE branches (5 root cause axes)
DROP VIEW IF EXISTS v_mece_payment_friction;
CREATE VIEW v_mece_payment_friction AS
SELECT
    payment_method,
    paperless_billing,
    COUNT(*) AS n,
    AVG(churn_flag * 1.0) AS churn_rate,
    AVG(monthly_charges) AS avg_monthly
FROM fact_customer_state
GROUP BY payment_method, paperless_billing;

-- ANALYZE: Feature adoption paradox
DROP VIEW IF EXISTS v_feature_adoption_curve;
CREATE VIEW v_feature_adoption_curve AS
SELECT
    features_adopted,
    COUNT(*) AS n,
    AVG(churn_flag * 1.0) AS churn_rate,
    AVG(monthly_charges) AS avg_monthly,
    AVG(tenure_months) AS avg_tenure
FROM fact_customer_state
GROUP BY features_adopted;

-- IMPROVE: STP segmentation (4 actionable segments)
DROP VIEW IF EXISTS v_stp_segments;
CREATE VIEW v_stp_segments AS
SELECT
    CASE
        WHEN tenure_months > 24 AND monthly_charges > 70 AND contract_type != 'Month-to-month'
            THEN 'High Value Loyalists'
        WHEN monthly_charges > 80 AND contract_type = 'Month-to-month'
            THEN 'At-Risk High Spenders'
        WHEN features_adopted <= 1 AND tenure_months < 12
            THEN 'Low Engagement Newcomers'
        WHEN tenure_months > 48 AND contract_type = 'Two year' AND monthly_charges < 60
            THEN 'Sticky Basics'
        ELSE 'Mainstream'
    END AS segment,
    COUNT(*) AS n,
    AVG(churn_flag * 1.0) AS churn_rate,
    AVG(monthly_charges) AS avg_monthly,
    AVG(tenure_months) AS avg_tenure,
    AVG(monthly_charges) * AVG(tenure_months) AS estimated_ltv
FROM fact_customer_state
GROUP BY segment;

-- CONTROL: Demographic + Contract risk grid
DROP VIEW IF EXISTS v_demographic_risk_grid;
CREATE VIEW v_demographic_risk_grid AS
SELECT
    senior_citizen,
    contract_type,
    COUNT(*) AS n,
    AVG(churn_flag * 1.0) AS churn_rate,
    AVG(monthly_charges) AS avg_monthly
FROM fact_customer_state
GROUP BY senior_citizen, contract_type;
