-- =====================================================================
-- Question 6 — Identify Accounts With Zero Recorded Feature Usage
-- Dataset: RavenStack SaaS Analytics
-- =====================================================================
--
-- Goal: find every account that has registered (exists in `accounts`)
--       but has no rows in `feature_usage` for any of its subscriptions.
--
-- Why LEFT JOIN (not INNER JOIN):
--   INNER JOIN silently drops accounts with no feature_usage rows —
--   exactly the rows we are trying to find. LEFT JOIN preserves every
--   account, fills feature_usage columns with NULL where there is no
--   match, and the WHERE fu.usage_id IS NULL filter keeps only the
--   unmatched accounts. This is the canonical SQL "anti-join" pattern.
--
-- Schema path:
--   accounts (1) ───< subscriptions (1) ───< feature_usage (many)
--   So we need TWO LEFT JOINs to walk the chain.
-- =====================================================================

-- ---------------------------------------------------------------------
-- Primary query — list of zero-activity accounts
-- ---------------------------------------------------------------------
SELECT
    a.account_id,
    a.account_name,
    a.industry,
    a.country,
    a.plan_tier,
    a.signup_date,
    a.is_trial,
    a.churn_flag
FROM accounts a
LEFT JOIN subscriptions  s  ON a.account_id      = s.account_id
LEFT JOIN feature_usage  fu ON s.subscription_id = fu.subscription_id
WHERE fu.usage_id IS NULL
ORDER BY a.signup_date DESC;


-- ---------------------------------------------------------------------
-- Equivalent expressed with NOT EXISTS (often faster on large tables
-- because the optimizer can short-circuit on the first match)
-- ---------------------------------------------------------------------
-- SELECT
--     a.account_id,
--     a.account_name,
--     a.industry,
--     a.plan_tier,
--     a.signup_date
-- FROM accounts a
-- WHERE NOT EXISTS (
--     SELECT 1
--     FROM subscriptions  s
--     JOIN feature_usage  fu ON s.subscription_id = fu.subscription_id
--     WHERE s.account_id = a.account_id
-- )
-- ORDER BY a.signup_date DESC;


-- ---------------------------------------------------------------------
-- Bonus: count zero-activity accounts by plan tier (executive summary)
-- ---------------------------------------------------------------------
SELECT
    a.plan_tier,
    COUNT(DISTINCT a.account_id) AS zero_activity_accounts
FROM accounts a
LEFT JOIN subscriptions  s  ON a.account_id      = s.account_id
LEFT JOIN feature_usage  fu ON s.subscription_id = fu.subscription_id
WHERE fu.usage_id IS NULL
GROUP BY a.plan_tier
ORDER BY zero_activity_accounts DESC;


-- =====================================================================
-- Result against the RavenStack dataset
-- =====================================================================
-- Total zero-activity accounts: 33 (out of 500 total accounts = 6.6%)
--
-- Sample (most recent signups):
--   account_id | industry      | plan_tier   | signup_date
--   -----------+---------------+-------------+------------
--   A-0f6450   | FinTech       | Pro         | 2024-12-27
--   A-671f31   | DevTools      | Basic       | 2024-11-24
--   A-712426   | HealthTech    | Enterprise  | 2024-11-10  <- urgent (Enterprise)
--   A-5c9849   | EdTech        | Basic       | 2024-11-03
--   A-c37601   | EdTech        | Basic       | 2024-10-31
--   ...
--
-- Action: highest-priority targets for activation campaigns; the
--         Enterprise account in particular should be contacted by CSM
--         within 48 hours given the revenue at risk.
-- =====================================================================
