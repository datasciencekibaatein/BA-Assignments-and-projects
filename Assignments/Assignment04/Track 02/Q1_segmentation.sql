-- =====================================================================
-- Question 1 — Market Segmentation: Spend & Engagement by User Group
-- Dataset: RavenStack SaaS (5 relational tables)
-- =====================================================================
--
-- Business context:
--   STP starts with measurable Segmentation. Aggregate spend (MRR) and
--   engagement (feature usage volume) per group to compare segments
--   on the two dimensions that matter for SaaS GTM strategy.
--
-- Tables joined:
--   accounts            → demographic / firmographic dimensions
--   subscriptions       → spend (MRR)
--   feature_usage       → engagement (usage events) via subscription_id
-- =====================================================================


-- ---------------------------------------------------------------------
-- Segmentation by PLAN TIER
-- ---------------------------------------------------------------------
WITH spend_per_account AS (
    SELECT
        account_id,
        SUM(mrr_amount) AS total_mrr,
        AVG(mrr_amount) AS avg_mrr_per_sub
    FROM ravenstack_subscriptions
    GROUP BY account_id
),
usage_per_account AS (
    SELECT
        s.account_id,
        SUM(fu.usage_count) AS total_usage,
        COUNT(fu.usage_id)  AS sessions
    FROM ravenstack_feature_usage fu
    JOIN ravenstack_subscriptions s ON fu.subscription_id = s.subscription_id
    GROUP BY s.account_id
)
SELECT
    a.plan_tier,
    COUNT(DISTINCT a.account_id)                AS n_accounts,
    ROUND(AVG(spa.avg_mrr_per_sub)::numeric, 0) AS avg_mrr,
    ROUND(AVG(spa.total_mrr)::numeric, 0)       AS avg_total_mrr,
    ROUND(AVG(upa.total_usage)::numeric, 0)     AS avg_usage_units,
    ROUND(AVG(upa.sessions)::numeric, 0)        AS avg_sessions,
    ROUND(AVG(CASE WHEN a.churn_flag THEN 1.0 ELSE 0.0 END) * 100, 2)
                                                AS churn_pct
FROM ravenstack_accounts a
LEFT JOIN spend_per_account spa ON a.account_id = spa.account_id
LEFT JOIN usage_per_account upa ON a.account_id = upa.account_id
GROUP BY a.plan_tier
ORDER BY avg_total_mrr DESC;


-- ---------------------------------------------------------------------
-- Segmentation by INDUSTRY (richer signal than plan_tier)
-- ---------------------------------------------------------------------
WITH spend_per_account AS (
    SELECT account_id, AVG(mrr_amount) AS avg_mrr_per_sub
    FROM ravenstack_subscriptions
    GROUP BY account_id
),
usage_per_account AS (
    SELECT s.account_id, SUM(fu.usage_count) AS total_usage
    FROM ravenstack_feature_usage fu
    JOIN ravenstack_subscriptions s ON fu.subscription_id = s.subscription_id
    GROUP BY s.account_id
)
SELECT
    a.industry,
    COUNT(DISTINCT a.account_id)                AS n_accounts,
    ROUND(AVG(spa.avg_mrr_per_sub)::numeric, 0) AS avg_mrr,
    ROUND(AVG(upa.total_usage)::numeric, 0)     AS avg_usage,
    ROUND(AVG(CASE WHEN a.churn_flag THEN 1.0 ELSE 0.0 END) * 100, 2)
                                                AS churn_pct
FROM ravenstack_accounts a
LEFT JOIN spend_per_account spa ON a.account_id = spa.account_id
LEFT JOIN usage_per_account upa ON a.account_id = upa.account_id
GROUP BY a.industry
ORDER BY churn_pct ASC, avg_mrr DESC;


-- =====================================================================
-- RESULTS (verified)
-- =====================================================================
-- BY PLAN TIER (homogeneous — limited segmentation signal):
--   Plan Tier  | n   | Avg MRR | Avg Total MRR | Avg Usage | Churn %
--   Basic      | 168 | $2,321  | $24,094       | 528.6     | 22.0%
--   Pro        | 178 | $2,266  | $22,296       | 484.5     | 21.9%
--   Enterprise | 154 | $2,200  | $21,572       | 490.1     | 22.1%
--
-- BY INDUSTRY (real differentiation visible):
--   Industry      | n   | Avg MRR | Avg Usage | Churn %
--   Cybersecurity | 100 | $2,307  | 504       | 16.0%   <- Best target (low churn)
--   EdTech        |  79 | $2,588  | 506       | 16.5%   <- Best target (high spend + low churn)
--   FinTech       | 112 | $2,372  | 499       | 22.3%
--   HealthTech    |  96 | $2,113  | 488       | 21.9%
--   DevTools      | 113 | $2,023  | 508       | 31.0%   <- Avoid (low spend + high churn)
--
-- KEY INSIGHT:
--   Plan-tier segmentation reveals NO meaningful behavioral differences
--   (all tiers show ~22% churn and ~$2,300 MRR). This means plan tier
--   is a SELF-SELECTED label that doesn't drive behavior — the real
--   segmentation signal is INDUSTRY VERTICAL.
--
--   Targeting recommendation: Focus GTM investment on EdTech and
--   Cybersecurity verticals; deprioritize DevTools.
-- =====================================================================
