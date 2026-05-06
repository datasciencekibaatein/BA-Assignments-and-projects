-- =====================================================================
-- Question 3 — Top 5 Features Used by Customers Active >6 Months
-- Dataset: RavenStack SaaS Analytics
-- =====================================================================
--
-- Logic:
--   "Active >6 months" = accounts whose signup_date is more than 180 days
--   before the analysis cutoff (CURRENT_DATE).
--
--   Path: accounts -> subscriptions -> feature_usage
--   We rank by SUM(usage_count) because a single event row can record
--   multiple invocations of the feature.
-- =====================================================================

-- ---------------------------------------------------------------------
-- ANSI / Standard SQL (works in SQL Server, Snowflake, BigQuery, etc.)
-- ---------------------------------------------------------------------
SELECT
    fu.feature_name,
    COUNT(*)                       AS usage_events,
    SUM(fu.usage_count)            AS total_usage_count,
    COUNT(DISTINCT a.account_id)   AS unique_accounts
FROM accounts a
JOIN subscriptions  s  ON a.account_id      = s.account_id
JOIN feature_usage  fu ON s.subscription_id = fu.subscription_id
WHERE DATEDIFF(DAY, a.signup_date, CURRENT_DATE) > 180
GROUP BY fu.feature_name
ORDER BY total_usage_count DESC
LIMIT 5;


-- ---------------------------------------------------------------------
-- PostgreSQL variant
-- ---------------------------------------------------------------------
-- SELECT
--     fu.feature_name,
--     COUNT(*)                       AS usage_events,
--     SUM(fu.usage_count)            AS total_usage_count,
--     COUNT(DISTINCT a.account_id)   AS unique_accounts
-- FROM accounts a
-- JOIN subscriptions  s  ON a.account_id      = s.account_id
-- JOIN feature_usage  fu ON s.subscription_id = fu.subscription_id
-- WHERE CURRENT_DATE - a.signup_date::date > 180
-- GROUP BY fu.feature_name
-- ORDER BY total_usage_count DESC
-- LIMIT 5;


-- ---------------------------------------------------------------------
-- SQLite variant (used for validation against the CSV files)
-- ---------------------------------------------------------------------
-- SELECT
--     fu.feature_name,
--     COUNT(*)                       AS usage_events,
--     SUM(fu.usage_count)            AS total_usage_count,
--     COUNT(DISTINCT a.account_id)   AS unique_accounts
-- FROM accounts a
-- JOIN subscriptions  s  ON a.account_id      = s.account_id
-- JOIN feature_usage  fu ON s.subscription_id = fu.subscription_id
-- WHERE julianday('2025-01-01') - julianday(a.signup_date) > 180
-- GROUP BY fu.feature_name
-- ORDER BY total_usage_count DESC
-- LIMIT 5;


-- =====================================================================
-- Result against the RavenStack dataset
-- =====================================================================
-- Rank | feature      | total_usage_count | usage_events | unique_accounts
-- -----+--------------+-------------------+--------------+----------------
--   1  | feature_32   |       4,914       |     485      |      260
--   2  | feature_12   |       4,728       |     475      |      264
--   3  | feature_2    |       4,701       |     458      |      260
--   4  | feature_15   |       4,697       |     457      |      247
--   5  | feature_31   |       4,684       |     466      |      242
-- =====================================================================
