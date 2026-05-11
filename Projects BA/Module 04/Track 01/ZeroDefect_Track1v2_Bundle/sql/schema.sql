-- ============================================================================
-- Olist Marketplace Operations - 3NF Schema + Analytical Views
-- For the Zero-Defect Initiative audit (Track 1)
-- SQLite-compatible. Run in order: tables, views.
-- ============================================================================

-- ---------- BASE TABLES ----------

DROP TABLE IF EXISTS order_reviews;
DROP TABLE IF EXISTS order_payments;
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS product_categories;
DROP TABLE IF EXISTS sellers;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id          TEXT PRIMARY KEY,
    customer_unique_id   TEXT,
    customer_zip_prefix  TEXT,
    customer_city        TEXT,
    customer_state       TEXT
);

CREATE TABLE sellers (
    seller_id            TEXT PRIMARY KEY,
    seller_zip_prefix    TEXT,
    seller_city          TEXT,
    seller_state         TEXT
);

CREATE TABLE product_categories (
    category_pt          TEXT PRIMARY KEY,
    category_en          TEXT
);

CREATE TABLE products (
    product_id           TEXT PRIMARY KEY,
    category_pt          TEXT,
    name_length          INTEGER,
    desc_length          INTEGER,
    photos_qty           INTEGER,
    weight_g             REAL,
    length_cm            REAL,
    height_cm            REAL,
    width_cm             REAL,
    FOREIGN KEY (category_pt) REFERENCES product_categories(category_pt)
);

CREATE TABLE orders (
    order_id             TEXT PRIMARY KEY,
    customer_id          TEXT NOT NULL,
    order_status         TEXT,
    purchase_ts          TIMESTAMP,
    approved_ts          TIMESTAMP,
    carrier_pickup_ts    TIMESTAMP,
    customer_delivered_ts TIMESTAMP,
    estimated_delivery_ts TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_id             TEXT,
    item_seq             INTEGER,
    product_id           TEXT,
    seller_id            TEXT,
    shipping_limit_ts    TIMESTAMP,
    price                REAL,
    freight_value        REAL,
    PRIMARY KEY (order_id, item_seq),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

CREATE TABLE order_payments (
    order_id             TEXT,
    payment_seq          INTEGER,
    payment_type         TEXT,
    payment_installments INTEGER,
    payment_value        REAL,
    PRIMARY KEY (order_id, payment_seq),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE order_reviews (
    review_id            TEXT,
    order_id             TEXT,
    review_score         INTEGER,
    review_creation_ts   TIMESTAMP,
    review_answer_ts     TIMESTAMP,
    PRIMARY KEY (review_id, order_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Indexes
CREATE INDEX idx_orders_customer    ON orders(customer_id);
CREATE INDEX idx_orders_status      ON orders(order_status);
CREATE INDEX idx_orders_purchase    ON orders(purchase_ts);
CREATE INDEX idx_items_seller       ON order_items(seller_id);
CREATE INDEX idx_items_product      ON order_items(product_id);
CREATE INDEX idx_reviews_order      ON order_reviews(order_id);
CREATE INDEX idx_customers_state    ON customers(customer_state);
CREATE INDEX idx_sellers_state      ON sellers(seller_state);


-- ---------- ANALYTICAL VIEWS ----------

DROP VIEW IF EXISTS v_order_lead_times;
DROP VIEW IF EXISTS v_state_performance;
DROP VIEW IF EXISTS v_seller_performance;
DROP VIEW IF EXISTS v_category_performance;
DROP VIEW IF EXISTS v_daily_order_volume;
DROP VIEW IF EXISTS v_review_vs_delay;

-- One row per delivered order with all process times in days (or hours for approval)
CREATE VIEW v_order_lead_times AS
SELECT
    o.order_id,
    o.customer_id,
    c.customer_state,
    o.purchase_ts,
    o.approved_ts,
    o.carrier_pickup_ts,
    o.customer_delivered_ts,
    o.estimated_delivery_ts,
    -- Process times
    (julianday(o.approved_ts) - julianday(o.purchase_ts)) * 24.0 AS approval_hours,
    julianday(o.carrier_pickup_ts) - julianday(o.approved_ts)    AS fulfillment_days,
    julianday(o.customer_delivered_ts) - julianday(o.carrier_pickup_ts) AS transit_days,
    julianday(o.customer_delivered_ts) - julianday(o.purchase_ts)       AS lead_time_days,
    -- Promise tracking
    julianday(o.estimated_delivery_ts) - julianday(o.purchase_ts)       AS estimate_buffer_days,
    julianday(o.customer_delivered_ts) - julianday(o.estimated_delivery_ts) AS delivery_delay_days,
    CASE WHEN julianday(o.customer_delivered_ts) > julianday(o.estimated_delivery_ts)
         THEN 1 ELSE 0 END AS is_late
FROM orders o
LEFT JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered'
  AND o.approved_ts          IS NOT NULL
  AND o.carrier_pickup_ts    IS NOT NULL
  AND o.customer_delivered_ts IS NOT NULL
  AND o.estimated_delivery_ts IS NOT NULL
  AND julianday(o.customer_delivered_ts) >= julianday(o.purchase_ts)
  AND julianday(o.carrier_pickup_ts)     >= julianday(o.approved_ts)
  AND julianday(o.customer_delivered_ts) >= julianday(o.carrier_pickup_ts);


-- State-level KPIs
CREATE VIEW v_state_performance AS
SELECT
    customer_state,
    COUNT(*)                                     AS n_orders,
    AVG(lead_time_days)                          AS mean_lead_days,
    AVG(fulfillment_days)                        AS mean_fulfillment_days,
    AVG(transit_days)                            AS mean_transit_days,
    1.0*SUM(is_late)/COUNT(*)                    AS pct_late
FROM v_order_lead_times
GROUP BY customer_state;


-- Seller-level KPIs (joined via order_items, primary seller = first item)
CREATE VIEW v_seller_performance AS
WITH primary_seller AS (
    SELECT order_id, MIN(seller_id) AS seller_id
    FROM order_items
    WHERE item_seq = 1
    GROUP BY order_id
)
SELECT
    s.seller_id,
    s.seller_state,
    COUNT(*)                          AS n_orders,
    AVG(lt.lead_time_days)            AS mean_lead_days,
    AVG(lt.fulfillment_days)          AS mean_fulfillment_days,
    1.0*SUM(lt.is_late)/COUNT(*)      AS pct_late
FROM v_order_lead_times lt
JOIN primary_seller ps ON lt.order_id = ps.order_id
JOIN sellers s ON ps.seller_id = s.seller_id
GROUP BY s.seller_id, s.seller_state
HAVING COUNT(*) >= 10;


-- Category-level KPIs
CREATE VIEW v_category_performance AS
WITH order_cat AS (
    SELECT oi.order_id, MIN(p.category_pt) AS category_pt
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    WHERE oi.item_seq = 1
    GROUP BY oi.order_id
)
SELECT
    pc.category_en,
    COUNT(*)                          AS n_orders,
    AVG(lt.lead_time_days)            AS mean_lead_days,
    1.0*SUM(lt.is_late)/COUNT(*)      AS pct_late
FROM v_order_lead_times lt
JOIN order_cat oc ON lt.order_id = oc.order_id
JOIN product_categories pc ON oc.category_pt = pc.category_pt
GROUP BY pc.category_en
HAVING COUNT(*) >= 30;


-- Daily order volume (for SARIMA)
CREATE VIEW v_daily_order_volume AS
SELECT
    DATE(purchase_ts) AS order_date,
    COUNT(*)          AS n_orders,
    AVG(lead_time_days) AS mean_lead,
    1.0*SUM(is_late)/COUNT(*) AS pct_late
FROM v_order_lead_times
GROUP BY DATE(purchase_ts);


-- Review score vs delay (the bombshell finding)
CREATE VIEW v_review_vs_delay AS
SELECT
    CASE
        WHEN delivery_delay_days <= 0 THEN '1. On-time'
        WHEN delivery_delay_days <= 3 THEN '2. Late 1-3 days'
        WHEN delivery_delay_days <= 7 THEN '3. Late 4-7 days'
        ELSE                                 '4. Late 8+ days'
    END AS delay_band,
    COUNT(*)              AS n_orders,
    AVG(r.review_score)   AS mean_score,
    1.0*SUM(CASE WHEN r.review_score <= 2 THEN 1 ELSE 0 END)/COUNT(*) AS pct_negative_review
FROM v_order_lead_times lt
LEFT JOIN order_reviews r ON lt.order_id = r.order_id
WHERE r.review_score IS NOT NULL
GROUP BY delay_band
ORDER BY delay_band;
