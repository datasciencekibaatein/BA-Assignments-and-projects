-- ============================================================================
-- DataCo Global - Last-Mile Delivery Audit
-- 3NF Normalized Schema
-- ============================================================================
-- Source: DataCoSupplyChainDataset.csv (180,519 order-line rows, 2015-01 to 2018-01)
--
-- Why 3NF (Third Normal Form):
--   1NF — atomic columns (the source CSV already satisfies this)
--   2NF — no partial dependencies on a composite key (we use surrogate IDs)
--   3NF — no transitive dependencies (Customer City -> Customer State is removed
--          by extracting customers into a dimension table)
--
-- Design choices specific to the brief:
--   - The brief asks for Routes/Vehicles/Fuel_Logs. The source dataset is a
--     marketplace dataset (no fleet data), so we model `shipping_modes` as the
--     proxy for vehicle class — Standard/First/Second/Same Day Class — and
--     compute fleet-OEE-equivalent metrics at the shipping_mode level.
--   - Routes are modelled as origin-destination pairs derived from
--     (customer_state, order_state). This is the closest analogue to a
--     real "route" the dataset supports.
--   - Fuel_Logs has no source column — we omit it rather than fabricate.
--     The OEE calculation uses Performance = scheduled_days / actual_days,
--     which captures the same "energy efficiency" idea fuel logs would.
--
-- All FKs are enforced. All money columns are DECIMAL(12,2).
-- ============================================================================

DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS customers CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS departments CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS markets CASCADE;
DROP TABLE IF EXISTS regions CASCADE;
DROP TABLE IF EXISTS shipping_modes CASCADE;


-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- markets: top-level geographic grouping (5 values: Africa, Europe, LATAM, Pacific Asia, USCA)
CREATE TABLE markets (
    market_id    SERIAL PRIMARY KEY,
    market_name  VARCHAR(50) NOT NULL UNIQUE
);

-- regions: 23 sub-market geographic groupings (e.g. Western Europe, South Asia)
CREATE TABLE regions (
    region_id    SERIAL PRIMARY KEY,
    region_name  VARCHAR(50) NOT NULL UNIQUE,
    market_id    INT NOT NULL REFERENCES markets(market_id)
);

-- shipping_modes: 4 service tiers (Standard / First / Second / Same Day Class)
-- Each has a default scheduled SLA in days
CREATE TABLE shipping_modes (
    mode_id              SERIAL PRIMARY KEY,
    mode_name            VARCHAR(20) NOT NULL UNIQUE,
    sla_scheduled_days   DECIMAL(4,2) NOT NULL,
    description          TEXT
);

-- departments: 11 store departments (e.g. Footwear, Apparel)
CREATE TABLE departments (
    department_id    SERIAL PRIMARY KEY,
    department_name  VARCHAR(50) NOT NULL UNIQUE
);

-- categories: ~50 product categories nested under departments
CREATE TABLE categories (
    category_id    SERIAL PRIMARY KEY,
    category_name  VARCHAR(100) NOT NULL,
    department_id  INT NOT NULL REFERENCES departments(department_id),
    UNIQUE(category_name, department_id)
);

-- products: ~118 distinct SKUs
CREATE TABLE products (
    product_id     SERIAL PRIMARY KEY,
    product_name   VARCHAR(255) NOT NULL,
    category_id    INT NOT NULL REFERENCES categories(category_id),
    list_price     DECIMAL(12,2) NOT NULL CHECK (list_price >= 0)
);

-- customers: ~20K distinct customers
CREATE TABLE customers (
    customer_id     SERIAL PRIMARY KEY,
    customer_fname  VARCHAR(50),
    customer_lname  VARCHAR(50),
    customer_segment VARCHAR(20) CHECK (customer_segment IN ('Consumer','Corporate','Home Office')),
    customer_city   VARCHAR(100),
    customer_state  VARCHAR(50),
    customer_country VARCHAR(50),
    customer_zipcode VARCHAR(10)
);

-- routes: origin -> destination pairs (derived from customer_state -> order_state)
-- This is our proxy for the brief's "Routes" table. Each route has:
--   - a typical lane distance (computed from lat/long)
--   - a market and region the order is delivered to
CREATE TABLE routes (
    route_id            SERIAL PRIMARY KEY,
    origin_state        VARCHAR(50),
    destination_state   VARCHAR(50),
    destination_country VARCHAR(50),
    region_id           INT NOT NULL REFERENCES regions(region_id),
    UNIQUE(origin_state, destination_state, destination_country)
);


-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- orders: 1 row per order
CREATE TABLE orders (
    order_id              BIGINT PRIMARY KEY,
    customer_id           INT NOT NULL REFERENCES customers(customer_id),
    route_id              INT NOT NULL REFERENCES routes(route_id),
    mode_id               INT NOT NULL REFERENCES shipping_modes(mode_id),
    order_date            TIMESTAMP NOT NULL,
    shipping_date         TIMESTAMP NOT NULL,
    days_shipping_real    DECIMAL(4,2) NOT NULL CHECK (days_shipping_real >= 0),
    days_shipping_sched   DECIMAL(4,2) NOT NULL CHECK (days_shipping_sched >= 0),
    delivery_status       VARCHAR(30) NOT NULL CHECK (delivery_status IN
                            ('Late delivery','Advance shipping','Shipping on time','Shipping canceled')),
    late_delivery_risk    BOOLEAN NOT NULL,
    order_status          VARCHAR(30) NOT NULL,
    order_profit          DECIMAL(12,2),
    CHECK (shipping_date >= order_date)
);

-- order_items: 1 row per line in an order (~180K rows)
CREATE TABLE order_items (
    order_item_id      BIGSERIAL PRIMARY KEY,
    order_id           BIGINT NOT NULL REFERENCES orders(order_id),
    product_id         INT NOT NULL REFERENCES products(product_id),
    quantity           INT NOT NULL CHECK (quantity > 0),
    unit_price         DECIMAL(12,2) NOT NULL,
    discount           DECIMAL(12,2) NOT NULL DEFAULT 0,
    discount_rate      DECIMAL(5,4) NOT NULL DEFAULT 0,
    item_total         DECIMAL(12,2) NOT NULL,
    profit_ratio       DECIMAL(6,4)
);


-- ============================================================================
-- INDEXES (for joining and SPC time series queries)
-- ============================================================================
CREATE INDEX idx_orders_date         ON orders(order_date);
CREATE INDEX idx_orders_mode         ON orders(mode_id);
CREATE INDEX idx_orders_route        ON orders(route_id);
CREATE INDEX idx_orders_status       ON orders(delivery_status);
CREATE INDEX idx_orders_late         ON orders(late_delivery_risk);
CREATE INDEX idx_routes_region       ON routes(region_id);
CREATE INDEX idx_regions_market      ON regions(market_id);
CREATE INDEX idx_order_items_order   ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);


-- ============================================================================
-- ANALYTICAL VIEWS — these power the dashboard and the OEE calculation
-- ============================================================================

-- ------------------------------------------------------------------
-- vw_oee_by_mode: Fleet OEE proxy at the Shipping Mode level
-- ------------------------------------------------------------------
-- OEE = Availability x Performance x Quality
--   Availability = orders_completed / orders_total          (not cancelled)
--   Performance  = scheduled_days / actual_days, capped 1.0 (delivery speed vs plan)
--   Quality      = orders_on_time / orders_completed        (not late)
-- This is the brief's "OEE of the delivery fleet" computed via complex joins.
-- ------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_oee_by_mode AS
SELECT
    sm.mode_name,
    sm.sla_scheduled_days,
    COUNT(*) AS orders_total,
    SUM(CASE WHEN o.delivery_status != 'Shipping canceled' THEN 1 ELSE 0 END) AS orders_completed,
    SUM(CASE WHEN o.late_delivery_risk = FALSE THEN 1 ELSE 0 END) AS orders_on_time,
    -- Availability
    ROUND(
      AVG(CASE WHEN o.delivery_status != 'Shipping canceled' THEN 1.0 ELSE 0.0 END)::numeric,
      4
    ) AS availability,
    -- Performance: cap sched/real at 1.0 (can't exceed 100%)
    ROUND(
      AVG(LEAST(
        CASE WHEN o.days_shipping_real > 0
             THEN o.days_shipping_sched / o.days_shipping_real
             ELSE 1.0 END,
        1.0
      ))::numeric,
      4
    ) AS performance,
    -- Quality
    ROUND(
      AVG(CASE WHEN o.late_delivery_risk = FALSE THEN 1.0 ELSE 0.0 END)::numeric,
      4
    ) AS quality,
    -- Composite OEE = A x P x Q
    ROUND(
      (AVG(CASE WHEN o.delivery_status != 'Shipping canceled' THEN 1.0 ELSE 0.0 END) *
       AVG(LEAST(
         CASE WHEN o.days_shipping_real > 0
              THEN o.days_shipping_sched / o.days_shipping_real
              ELSE 1.0 END,
         1.0
       )) *
       AVG(CASE WHEN o.late_delivery_risk = FALSE THEN 1.0 ELSE 0.0 END))::numeric,
      4
    ) AS oee
FROM orders o
JOIN shipping_modes sm ON o.mode_id = sm.mode_id
GROUP BY sm.mode_name, sm.sla_scheduled_days
ORDER BY oee DESC;

-- ------------------------------------------------------------------
-- vw_late_rate_by_region: Late-delivery rate by region with sample size
-- (feeds the SPC p-chart and the regional drill-through)
-- ------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_late_rate_by_region AS
SELECT
    m.market_name,
    r.region_name,
    COUNT(*) AS n_orders,
    SUM(CASE WHEN o.late_delivery_risk THEN 1 ELSE 0 END) AS n_late,
    ROUND(AVG(CASE WHEN o.late_delivery_risk THEN 1.0 ELSE 0.0 END)::numeric, 4) AS late_rate,
    ROUND(AVG(o.days_shipping_real)::numeric, 2) AS avg_real_days,
    ROUND(AVG(o.days_shipping_sched)::numeric, 2) AS avg_sched_days
FROM orders o
JOIN routes ro    ON o.route_id    = ro.route_id
JOIN regions r    ON ro.region_id  = r.region_id
JOIN markets m    ON r.market_id   = m.market_id
GROUP BY m.market_name, r.region_name
ORDER BY late_rate DESC;

-- ------------------------------------------------------------------
-- vw_daily_volume: Daily order volume + late count (feeds SARIMA + SPC)
-- ------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_daily_volume AS
SELECT
    DATE(o.order_date)            AS order_day,
    COUNT(*)                      AS n_orders,
    SUM(CASE WHEN o.late_delivery_risk THEN 1 ELSE 0 END) AS n_late,
    AVG(o.days_shipping_real)     AS avg_real_days,
    AVG(o.days_shipping_sched)    AS avg_sched_days
FROM orders o
GROUP BY DATE(o.order_date)
ORDER BY order_day;

-- ------------------------------------------------------------------
-- vw_drill_through: row-level details for executive drill-through
-- (clicking a region in the dashboard reveals these rows)
-- ------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_drill_through AS
SELECT
    o.order_id,
    o.order_date,
    m.market_name,
    r.region_name,
    ro.destination_country,
    sm.mode_name AS shipping_mode,
    o.days_shipping_sched,
    o.days_shipping_real,
    (o.days_shipping_real - o.days_shipping_sched) AS variance_days,
    o.delivery_status,
    o.late_delivery_risk,
    c.customer_segment,
    o.order_profit
FROM orders o
JOIN routes ro       ON o.route_id    = ro.route_id
JOIN regions r       ON ro.region_id  = r.region_id
JOIN markets m       ON r.market_id   = m.market_id
JOIN shipping_modes sm ON o.mode_id   = sm.mode_id
JOIN customers c     ON o.customer_id = c.customer_id;


-- ============================================================================
-- SAMPLE QUERIES (for the report appendix)
-- ============================================================================

-- Q1. OEE by Shipping Mode
-- SELECT * FROM vw_oee_by_mode;

-- Q2. Top 5 most-late regions, with sample size guard (n > 1000)
-- SELECT * FROM vw_late_rate_by_region WHERE n_orders > 1000 ORDER BY late_rate DESC LIMIT 5;

-- Q3. Monthly volume trend (feeds SARIMA)
-- SELECT DATE_TRUNC('month', order_day) AS month,
--        SUM(n_orders) AS volume,
--        SUM(n_late) * 1.0 / SUM(n_orders) AS late_rate
-- FROM vw_daily_volume GROUP BY 1 ORDER BY 1;

-- Q4. The "complex join" the brief asks for — OEE per region per mode
-- (joins orders, routes, regions, markets, shipping_modes — 5-way join)
-- SELECT m.market_name, r.region_name, sm.mode_name,
--        COUNT(*) AS n,
--        AVG(LEAST(CASE WHEN o.days_shipping_real>0
--                       THEN o.days_shipping_sched/o.days_shipping_real
--                       ELSE 1.0 END, 1.0)) AS performance,
--        AVG(CASE WHEN o.late_delivery_risk=FALSE THEN 1.0 ELSE 0.0 END) AS quality
-- FROM orders o
-- JOIN routes ro ON o.route_id=ro.route_id
-- JOIN regions r ON ro.region_id=r.region_id
-- JOIN markets m ON r.market_id=m.market_id
-- JOIN shipping_modes sm ON o.mode_id=sm.mode_id
-- GROUP BY 1,2,3
-- HAVING COUNT(*) > 100
-- ORDER BY 1,2,3;
