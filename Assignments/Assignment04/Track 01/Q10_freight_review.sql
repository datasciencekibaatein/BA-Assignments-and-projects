-- =====================================================================
-- Question 10 — Freight Tier vs Review Score (Carrier Quality Proxy)
-- Dataset: Olist Brazilian E-Commerce
-- =====================================================================
--
-- Business context:
--   The dataset doesn't have an explicit "carrier_type" column, but
--   freight_value (shipping cost) is a strong proxy for carrier
--   service level — higher freight typically corresponds to longer
--   distances or premium carriers. We test whether higher freight
--   tiers correlate with worse customer review outcomes (a proxy for
--   damage / quality issues).
--
-- Tables joined:
--   olist_order_items_dataset.freight_value  → carrier proxy
--   olist_order_reviews_dataset.review_score → quality outcome
-- =====================================================================


-- ---------------------------------------------------------------------
-- Aggregate freight per order (sum across line items)
-- ---------------------------------------------------------------------
WITH order_freight AS (
    SELECT
        order_id,
        SUM(freight_value) AS total_freight
    FROM olist_order_items_dataset
    GROUP BY order_id
),
joined AS (
    SELECT
        f.order_id,
        f.total_freight,
        r.review_score,
        NTILE(4) OVER (ORDER BY f.total_freight) AS freight_tier
    FROM order_freight f
    JOIN olist_order_reviews_dataset r ON f.order_id = r.order_id
)
SELECT
    CASE freight_tier
        WHEN 1 THEN '1-Low'
        WHEN 2 THEN '2-Mid-Low'
        WHEN 3 THEN '3-Mid-High'
        WHEN 4 THEN '4-High'
    END                                              AS tier,
    COUNT(*)                                         AS order_count,
    ROUND(AVG(total_freight)::numeric, 2)            AS avg_freight_value,
    ROUND(AVG(review_score)::numeric, 3)             AS avg_review_score,
    ROUND(
        SUM(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
        2
    )                                                AS pct_low_review
FROM joined
GROUP BY freight_tier
ORDER BY freight_tier;


-- ---------------------------------------------------------------------
-- Pearson correlation freight_value vs review_score
-- ---------------------------------------------------------------------
WITH order_freight AS (
    SELECT order_id, SUM(freight_value) AS total_freight
    FROM olist_order_items_dataset
    GROUP BY order_id
),
joined AS (
    SELECT f.total_freight, r.review_score
    FROM order_freight f
    JOIN olist_order_reviews_dataset r ON f.order_id = r.order_id
)
SELECT
    CORR(total_freight, review_score) AS pearson_correlation,
    COUNT(*)                          AS pair_count
FROM joined;


-- =====================================================================
-- RESULTS (verified)
-- =====================================================================
-- Tier         | Count   | Avg Freight | Avg Review | % Low (1-2 stars)
-- 1-Low        | 24,623  | $10.45      | 4.26       | 10.52%
-- 2-Mid-Low    | 24,632  | $15.46      | 4.14       | 13.18%
-- 3-Mid-High   | 24,600  | $19.78      | 4.12       | 13.51%
-- 4-High       | 24,610  | $45.51      | 3.89       | 19.56%
--
-- Pearson correlation: -0.0886
-- (statistically significant negative relationship at this sample size)
--
-- INTERPRETATION:
--   - Higher freight (proxy for harder routes / premium carriers)
--     correlates with lower review scores
--   - High-freight orders have ~2x the rate of low reviews vs
--     low-freight orders (19.56% vs 10.52%)
--   - The correlation is weak (-0.09) but practically significant
--     given 98K+ paired observations
--
-- BUSINESS RECOMMENDATION:
--   The correlation suggests that "expensive shipping" maps to
--   "harder logistics" rather than "better service" — likely
--   because high freight = remote destination = longer transit
--   = more chances for damage/delay. Investigate whether high-
--   freight orders need:
--     - Additional protective packaging
--     - SLA extensions in customer-facing ETAs
--     - Alternative carrier selection logic
-- =====================================================================
