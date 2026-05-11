-- =====================================================================
-- DistributorCo Lean Shield (DMAIC) - SQLite Schema
-- =====================================================================
-- Source: DataCo Smart Supply Chain (180,519 orders, 2015-2018)
-- Purpose: Fact + dim model + 5 analytical views, one per DMAIC stage
-- =====================================================================

DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_warehouse;

-- =====================================================================
-- DIMENSION TABLES
-- =====================================================================

CREATE TABLE dim_product (
    product_card_id      INTEGER PRIMARY KEY,
    product_name         TEXT,
    category_id          INTEGER,
    category_name        TEXT,
    department_id        INTEGER,
    department_name      TEXT,
    product_price        REAL
);

CREATE TABLE dim_customer (
    customer_id          INTEGER PRIMARY KEY,
    customer_segment     TEXT,
    customer_country     TEXT,
    customer_state       TEXT,
    customer_city        TEXT
);

-- "Warehouse" = Market (5 regions = 5 fulfillment centers in our framing)
CREATE TABLE dim_warehouse (
    market_name          TEXT PRIMARY KEY,
    region               TEXT
);

-- =====================================================================
-- FACT TABLE
-- =====================================================================

CREATE TABLE fact_orders (
    order_item_id            INTEGER PRIMARY KEY,
    order_id                 INTEGER,
    order_date               TEXT,
    shipping_date            TEXT,
    customer_id              INTEGER,
    product_card_id          INTEGER,
    market                   TEXT,
    order_region             TEXT,
    order_country            TEXT,
    shipping_mode            TEXT,
    order_status             TEXT,
    delivery_status          TEXT,
    days_shipping_real       INTEGER,
    days_shipment_scheduled  INTEGER,
    late_delivery_risk       INTEGER,
    order_item_quantity      INTEGER,
    order_item_total         REAL,
    order_profit_per_order   REAL,
    sales                    REAL,
    type                     TEXT,
    FOREIGN KEY (customer_id)     REFERENCES dim_customer(customer_id),
    FOREIGN KEY (product_card_id) REFERENCES dim_product(product_card_id),
    FOREIGN KEY (market)          REFERENCES dim_warehouse(market_name)
);

CREATE INDEX idx_orders_date    ON fact_orders(order_date);
CREATE INDEX idx_orders_mode    ON fact_orders(shipping_mode);
CREATE INDEX idx_orders_market  ON fact_orders(market);
CREATE INDEX idx_orders_status  ON fact_orders(order_status);
CREATE INDEX idx_orders_product ON fact_orders(product_card_id);

-- =====================================================================
-- ANALYTICAL VIEWS - one per DMAIC stage
-- =====================================================================

-- DEFINE: Voice of customer (delivery defect rate by mode/market)
DROP VIEW IF EXISTS v_define_defect_rate;
CREATE VIEW v_define_defect_rate AS
SELECT
    shipping_mode,
    market,
    COUNT(*) AS n_orders,
    AVG(late_delivery_risk * 1.0) AS late_rate,
    AVG(days_shipping_real - days_shipment_scheduled) AS avg_overrun_days,
    SUM(order_profit_per_order) AS total_profit
FROM fact_orders
WHERE order_status NOT IN ('CANCELED', 'SUSPECTED_FRAUD')
GROUP BY shipping_mode, market;

-- MEASURE: Daily process metrics for SPC
DROP VIEW IF EXISTS v_measure_daily_spc;
CREATE VIEW v_measure_daily_spc AS
SELECT
    DATE(order_date) AS day,
    shipping_mode,
    COUNT(*) AS n,
    AVG(days_shipping_real * 1.0) AS xbar,
    -- Population std (will compute proper sample std in Python)
    AVG(late_delivery_risk * 1.0) AS p_late
FROM fact_orders
WHERE order_status NOT IN ('CANCELED', 'SUSPECTED_FRAUD')
GROUP BY DATE(order_date), shipping_mode;

-- ANALYZE: Order Status flow (BPMN state distribution)
DROP VIEW IF EXISTS v_analyze_state_dist;
CREATE VIEW v_analyze_state_dist AS
SELECT
    order_status,
    COUNT(*) AS n,
    AVG(order_profit_per_order) AS avg_profit,
    AVG(late_delivery_risk * 1.0) AS late_rate
FROM fact_orders
GROUP BY order_status;

-- IMPROVE: Top SKUs by demand for EOQ
DROP VIEW IF EXISTS v_improve_top_skus;
CREATE VIEW v_improve_top_skus AS
SELECT
    p.product_card_id,
    p.product_name,
    p.category_name,
    p.product_price,
    COUNT(*) AS total_orders,
    SUM(o.order_item_quantity) AS total_units,
    SUM(o.sales) AS total_revenue,
    AVG(o.days_shipping_real * 1.0) AS avg_lead_time
FROM fact_orders o
JOIN dim_product p ON o.product_card_id = p.product_card_id
WHERE o.order_status = 'COMPLETE'
GROUP BY p.product_card_id, p.product_name, p.category_name, p.product_price
ORDER BY total_units DESC;

-- CONTROL: Per-mode capability inputs (for Cpk calc in Python)
DROP VIEW IF EXISTS v_control_capability;
CREATE VIEW v_control_capability AS
SELECT
    shipping_mode,
    days_shipment_scheduled AS USL,
    0 AS LSL,
    AVG(days_shipping_real * 1.0) AS process_mean,
    COUNT(*) AS n,
    SUM(late_delivery_risk * 1.0) / COUNT(*) AS p_late
FROM fact_orders
WHERE order_status NOT IN ('CANCELED', 'SUSPECTED_FRAUD')
GROUP BY shipping_mode, days_shipment_scheduled;
