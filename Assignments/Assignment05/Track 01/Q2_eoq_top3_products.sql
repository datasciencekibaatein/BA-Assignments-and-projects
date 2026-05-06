-- =====================================================================
-- Question 2 — Economic Order Quantity (EOQ) for Top-3 Products
-- Dataset: DataCo Smart Supply Chain
-- =====================================================================
--
-- EOQ formula:
--   EOQ = sqrt(2 × D × S / H)
--   where D = annual demand, S = ordering cost per order,
--         H = annual holding cost per unit
--
-- Assumptions:
--   S = $50 per order (industry standard for SKU procurement)
--   H = 25% × unit price (industry standard holding cost — capital
--                          + storage + insurance + obsolescence)
-- =====================================================================


-- ---------------------------------------------------------------------
-- Identify top-3 products by total demand (3-year period)
-- ---------------------------------------------------------------------
SELECT
    "Product Name",
    SUM("Order Item Quantity")                          AS total_qty_3yr,
    ROUND((SUM("Order Item Quantity") / 3.0)::numeric, 0) AS annual_demand,
    COUNT(*)                                            AS n_orders,
    ROUND(AVG("Product Price")::numeric, 2)             AS avg_price
FROM dataco_supply_chain
GROUP BY "Product Name"
ORDER BY total_qty_3yr DESC
LIMIT 3;


-- ---------------------------------------------------------------------
-- EOQ calculation for top-3 products with sensitivity columns
-- ---------------------------------------------------------------------
WITH top_products AS (
    SELECT
        "Product Name",
        SUM("Order Item Quantity") / 3.0  AS annual_demand,
        AVG("Product Price")              AS unit_price
    FROM dataco_supply_chain
    GROUP BY "Product Name"
    ORDER BY SUM("Order Item Quantity") DESC
    LIMIT 3
),
eoq_calc AS (
    SELECT
        "Product Name",
        annual_demand,
        unit_price,
        50.0                              AS ordering_cost,
        unit_price * 0.25                 AS holding_cost_per_unit,
        SQRT(2 * annual_demand * 50.0 / (unit_price * 0.25))
                                          AS EOQ
    FROM top_products
)
SELECT
    "Product Name",
    ROUND(annual_demand::numeric, 0)              AS annual_demand,
    ROUND(unit_price::numeric, 2)                 AS unit_price,
    ROUND(holding_cost_per_unit::numeric, 2)      AS holding_cost_per_unit,
    ROUND(EOQ::numeric, 0)                        AS EOQ_units,
    ROUND((annual_demand / EOQ)::numeric, 1)      AS orders_per_year,
    -- Total annual cost at EOQ
    ROUND(((annual_demand / EOQ * 50.0) +
           (EOQ / 2 * unit_price * 0.25))::numeric, 0) AS total_annual_cost,
    -- Reorder point assuming 4-day lead time + 2-day safety stock
    ROUND(((annual_demand / 365) * 6)::numeric, 0) AS reorder_point_units
FROM eoq_calc
ORDER BY annual_demand DESC;


-- =====================================================================
-- RESULTS (verified)
-- =====================================================================
-- Top 3 products by annual demand (3-year average):
--
--   1. Perfect Fitness Perfect Rip Deck
--      Annual demand: 24,566 units | Price: $59.99
--      EOQ: 405 units | Total annual cost: $6,070
--      Reorder Point: 404 units (assuming 6-day lead time)
--
--   2. Nike Men's Dri-FIT Victory Golf Polo
--      Annual demand: 20,985 units | Price: $50.00
--      EOQ: 410 units | Total annual cost: $5,123
--      Reorder Point: 345 units
--
--   3. O'Brien Men's Neoprene Life Vest
--      Annual demand: 19,268 units | Price: $49.98
--      EOQ: 393 units | Total annual cost: $4,907
--      Reorder Point: 317 units
--
-- BUSINESS INTERPRETATION:
--   - Optimal order frequency: ~50-60 orders per year per product (~weekly)
--   - Total inventory cost across top-3 products: ~$16,100/year
--   - Even slight order quantity miscalibration (±20% from EOQ)
--     increases total cost by ~5-10% — discipline matters
--   - These EOQ values feed directly into the Q8 Kissflow reorder
--     workflow trigger thresholds.
-- =====================================================================
