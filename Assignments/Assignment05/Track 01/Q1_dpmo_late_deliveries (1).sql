-- =====================================================================
-- Question 1 — DMAIC Measure: DPMO for Late Deliveries
-- Dataset: DataCo Smart Supply Chain (180,519 orders × 53 columns)
-- =====================================================================
--
-- DMAIC framework:
--   D - Define: late delivery is the defect
--   M - MEASURE (this query): quantify defect rate as DPMO
--   A - Analyze: find drivers (Q4, Q9)
--   I - Improve: redesign carrier selection (Q9)
--   C - Control: Kissflow/Fabric automation (Q8, Q10)
--
-- DPMO = (Defects / Total Opportunities) × 1,000,000
-- One opportunity per order = each order can be late or on-time
-- =====================================================================


-- ---------------------------------------------------------------------
-- Overall DPMO for late deliveries
-- ---------------------------------------------------------------------
SELECT
    COUNT(*)                                                        AS total_orders,
    SUM(Late_delivery_risk)                                         AS late_deliveries,
    ROUND(AVG(Late_delivery_risk) * 100, 2)                         AS late_pct,
    ROUND((SUM(Late_delivery_risk) * 1000000.0 / COUNT(*))::numeric, 0)
                                                                    AS DPMO,
    -- Sigma level (without 1.5σ shift, then add 1.5)
    -- This is illustrative; full computation uses NORMSINV
    'See Python notebook for exact Sigma calculation'              AS sigma_level_note
FROM dataco_supply_chain;


-- ---------------------------------------------------------------------
-- DPMO by Shipping Mode — diagnostic for the Improve phase
-- ---------------------------------------------------------------------
SELECT
    "Shipping Mode",
    COUNT(*)                                                AS total_orders,
    SUM(Late_delivery_risk)                                 AS late_deliveries,
    ROUND(AVG(Late_delivery_risk) * 100, 2)                 AS late_pct,
    ROUND((SUM(Late_delivery_risk) * 1000000.0 / COUNT(*))::numeric, 0)
                                                            AS DPMO
FROM dataco_supply_chain
GROUP BY "Shipping Mode"
ORDER BY DPMO DESC;


-- ---------------------------------------------------------------------
-- DPMO by Market region
-- ---------------------------------------------------------------------
SELECT
    Market,
    COUNT(*)                                                AS total_orders,
    SUM(Late_delivery_risk)                                 AS late_deliveries,
    ROUND(AVG(Late_delivery_risk) * 100, 2)                 AS late_pct,
    ROUND((SUM(Late_delivery_risk) * 1000000.0 / COUNT(*))::numeric, 0)
                                                            AS DPMO
FROM dataco_supply_chain
GROUP BY Market
ORDER BY total_orders DESC;


-- ---------------------------------------------------------------------
-- DPMO by Department (Pareto identification)
-- ---------------------------------------------------------------------
SELECT
    "Department Name",
    COUNT(*)                                                AS total_orders,
    SUM(Late_delivery_risk)                                 AS late_deliveries,
    ROUND(AVG(Late_delivery_risk) * 100, 2)                 AS late_pct,
    ROUND((SUM(Late_delivery_risk) * 1000000.0 / COUNT(*))::numeric, 0)
                                                            AS DPMO
FROM dataco_supply_chain
GROUP BY "Department Name"
ORDER BY total_orders DESC
LIMIT 10;


-- =====================================================================
-- RESULTS (verified)
-- =====================================================================
-- Overall:
--   Total orders:      180,519
--   Late deliveries:    98,977
--   Late %:              54.83%
--   DPMO:               548,291
--   Sigma level:        ~1.38σ (with 1.5σ shift)
--   Six Sigma target:   3.4 DPMO (6.0σ) — gap of 4.62 sigma levels
--
-- By Shipping Mode (CRITICAL FINDING — counter-intuitive):
--   First Class:    953,225 DPMO (95.3% late) ← WORST despite being premium
--   Second Class:   766,328 DPMO (76.6% late)
--   Same Day:       457,430 DPMO (45.7% late)
--   Standard Class: 380,717 DPMO (38.1% late) ← BEST
--
-- BUSINESS INSIGHT:
--   The pricing/SLA structure is INVERTED. Customers who pay extra for
--   First Class get a worse outcome than Standard Class customers.
--   This is the smoking gun for the Improve phase: either the SLAs
--   are mis-set (over-promising) or the carrier selection process
--   routes premium orders to slow lanes.
-- =====================================================================
