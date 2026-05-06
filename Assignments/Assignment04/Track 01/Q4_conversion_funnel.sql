-- =====================================================================
-- Question 4 — Order-to-Delivery Conversion Funnel
-- Dataset: Olist Brazilian E-Commerce (olist_orders_dataset)
-- =====================================================================
--
-- Business context:
--   Quantify the drop-off at each stage of the order fulfillment
--   process. Each stage is marked by the presence of a timestamp
--   in the orders table — if a stage timestamp is NULL, that order
--   never reached that stage.
--
-- Funnel stages:
--   1. Purchased  → order_purchase_timestamp     (always present)
--   2. Approved   → order_approved_at            (NULL = payment failed)
--   3. Carrier    → order_delivered_carrier_date (NULL = warehouse never released)
--   4. Delivered  → order_delivered_customer_date(NULL = last-mile failure)
-- =====================================================================


-- ---------------------------------------------------------------------
-- Funnel counts at each stage
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                              AS stage_1_purchased,
    COUNT(order_approved_at)                              AS stage_2_approved,
    COUNT(order_delivered_carrier_date)                   AS stage_3_sent_to_carrier,
    COUNT(order_delivered_customer_date)                  AS stage_4_delivered_to_customer
FROM olist_orders_dataset;


-- ---------------------------------------------------------------------
-- Stage-by-stage drop-off percentages
-- ---------------------------------------------------------------------
WITH funnel AS (
    SELECT
        COUNT(*)                                   AS s1_purchased,
        COUNT(order_approved_at)                   AS s2_approved,
        COUNT(order_delivered_carrier_date)        AS s3_carrier,
        COUNT(order_delivered_customer_date)       AS s4_delivered
    FROM olist_orders_dataset
)
SELECT
    'Purchased -> Approved'   AS transition,
    s1_purchased              AS from_count,
    s2_approved               AS to_count,
    ROUND((s1_purchased - s2_approved) * 100.0 / s1_purchased, 2)  AS dropoff_pct
FROM funnel
UNION ALL
SELECT
    'Approved -> Carrier',
    s2_approved,
    s3_carrier,
    ROUND((s2_approved - s3_carrier) * 100.0 / s2_approved, 2)
FROM funnel
UNION ALL
SELECT
    'Carrier -> Delivered',
    s3_carrier,
    s4_delivered,
    ROUND((s3_carrier - s4_delivered) * 100.0 / s3_carrier, 2)
FROM funnel;


-- ---------------------------------------------------------------------
-- Cancelled & unavailable orders by stage they failed at
-- ---------------------------------------------------------------------
SELECT
    order_status,
    COUNT(*)                                              AS order_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 3)    AS pct_of_total
FROM olist_orders_dataset
GROUP BY order_status
ORDER BY order_count DESC;


-- =====================================================================
-- RESULTS (verified)
-- =====================================================================
-- Stage counts:
--   1. Purchased:               99,441 (100.00%)
--   2. Approved:                99,281  (99.84%)  -- 0.16% drop-off
--   3. Sent to Carrier:         97,658  (98.21%)  -- 1.63% drop-off (LARGEST LEAK)
--   4. Delivered to Customer:   96,476  (97.02%)  -- 1.21% drop-off
--
-- Total funnel completion: 97.02% (3% loss across all stages)
--
-- Order status breakdown:
--   delivered:    96,478  (97.02%)
--   shipped:       1,107   (1.11%)
--   canceled:        625   (0.63%)
--   unavailable:     609   (0.61%)
--   invoiced:        314   (0.32%)
--   processing:      301   (0.30%)
--   created:           5   (0.01%)
--   approved:          2   (0.00%)
--
-- INTERPRETATION:
--   The largest leak is at Approved → Carrier (1.63%) — meaning the
--   warehouse-to-logistics handoff is where 1,623 orders die. This
--   is a process design problem: warehouse picking, packing, and
--   carrier scheduling are not tightly synchronised.
--
--   Recommendation: introduce a same-day handoff SLA between
--   warehouse and carrier, monitored by the order_delivered_carrier_date
--   timestamp gap. Target: reduce 1.63% drop-off to <0.5%.
-- =====================================================================
