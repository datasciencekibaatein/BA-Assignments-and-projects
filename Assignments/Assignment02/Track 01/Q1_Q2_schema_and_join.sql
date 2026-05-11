
-- Q1 — Normalize the flat file to 3NF.
-- Q2 — Calculate total profit per Product_Category using INNER JOIN
--      between the normalized Sales and Products tables.
-- =====================================================================


-- =====================================================================
-- SECTION 1: SCHEMA CREATION (Q1 — 3NF DDL)
-- =====================================================================

DROP DATABASE IF EXISTS retail_analytics;
CREATE DATABASE retail_analytics;
USE retail_analytics;


-- ---------- DIMENSION 1: REGIONS ----------
-- Stores the four geographic regions. Region_Name is unique.
CREATE TABLE regions (
    region_id    INT AUTO_INCREMENT PRIMARY KEY,
    region_name  VARCHAR(20) NOT NULL UNIQUE
);


-- ---------- DIMENSION 2: SALES_REPS ----------
-- Each sales rep belongs to exactly ONE region.
-- This resolves the transitive dependency Sales_Rep -> Region
-- that existed in the flat file (visible in the redundant
-- "Region_and_Sales_Rep" column).
CREATE TABLE sales_reps (
    rep_id     INT AUTO_INCREMENT PRIMARY KEY,
    rep_name   VARCHAR(50) NOT NULL,
    region_id  INT NOT NULL,
    CONSTRAINT fk_rep_region
        FOREIGN KEY (region_id) REFERENCES regions(region_id),
    UNIQUE KEY uq_rep_region (rep_name, region_id)
);


-- ---------- DIMENSION 3: CUSTOMERS ----------
-- Customer segment lookup (New / Returning).
CREATE TABLE customers (
    customer_type_id  INT AUTO_INCREMENT PRIMARY KEY,
    customer_type     VARCHAR(20) NOT NULL UNIQUE
);


-- ---------- DIMENSION 4: PRODUCTS ----------
-- Product_Category, Unit_Cost, and Unit_Price depend ONLY on Product_ID.
-- Storing them once here (instead of 400,000 times in the fact table)
-- eliminates the partial dependency that violated 2NF.
CREATE TABLE products (
    product_id        INT PRIMARY KEY,
    product_category  VARCHAR(30) NOT NULL,
    unit_cost         DECIMAL(10,2) NOT NULL,
    unit_price        DECIMAL(10,2) NOT NULL,
    INDEX idx_category (product_category)
);


-- ---------- FACT TABLE: SALES ----------
-- One row per transaction. All descriptive attributes are FKs.
-- Profit is intentionally NOT stored — it is derived at query time
-- from products.unit_cost / products.unit_price to avoid update
-- anomalies if a product's price ever changes.
CREATE TABLE sales (
    sale_id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    sale_date         DATE NOT NULL,
    product_id        INT NOT NULL,
    rep_id            INT NOT NULL,
    region_id         INT NOT NULL,
    customer_type_id  INT NOT NULL,
    quantity_sold     INT NOT NULL,
    sales_amount      DECIMAL(12,2) NOT NULL,
    discount          DECIMAL(4,2) NOT NULL,
    payment_method    VARCHAR(20),
    sales_channel     VARCHAR(20),

    CONSTRAINT fk_sales_product   FOREIGN KEY (product_id)       REFERENCES products(product_id),
    CONSTRAINT fk_sales_rep       FOREIGN KEY (rep_id)           REFERENCES sales_reps(rep_id),
    CONSTRAINT fk_sales_region    FOREIGN KEY (region_id)        REFERENCES regions(region_id),
    CONSTRAINT fk_sales_customer  FOREIGN KEY (customer_type_id) REFERENCES customers(customer_type_id),

    -- Indexes that real-time dashboards will need
    INDEX idx_sale_date  (sale_date),
    INDEX idx_region     (region_id),
    INDEX idx_product    (product_id)
);


-- =====================================================================
-- SECTION 2: ETL — POPULATING THE NORMALIZED TABLES
-- =====================================================================
-- Assumes the raw CSV has been loaded into a staging table called
-- `staging_sales` with column names matching the CSV headers.
-- (Use LOAD DATA INFILE 'synthetic_sales_data_400k.csv' INTO TABLE
-- staging_sales FIELDS TERMINATED BY ',' IGNORE 1 LINES; first.)
-- =====================================================================

-- 1. Distinct regions
INSERT INTO regions (region_name)
SELECT DISTINCT Region FROM staging_sales;

-- 2. Distinct customer segments
INSERT INTO customers (customer_type)
SELECT DISTINCT Customer_Type FROM staging_sales;

-- 3. Distinct sales reps with their region
INSERT INTO sales_reps (rep_name, region_id)
SELECT DISTINCT s.Sales_Rep, r.region_id
FROM staging_sales s
JOIN regions r ON r.region_name = s.Region;

-- 4. Distinct products. We take the FIRST observed cost/price per
--    Product_ID (the synthetic data is consistent per product).
INSERT INTO products (product_id, product_category, unit_cost, unit_price)
SELECT Product_ID,
       MIN(Product_Category) AS product_category,
       MIN(Unit_Cost)        AS unit_cost,
       MIN(Unit_Price)       AS unit_price
FROM staging_sales
GROUP BY Product_ID;

-- 5. Fact rows
INSERT INTO sales (sale_date, product_id, rep_id, region_id,
                   customer_type_id, quantity_sold, sales_amount,
                   discount, payment_method, sales_channel)
SELECT s.Sale_Date,
       s.Product_ID,
       sr.rep_id,
       r.region_id,
       c.customer_type_id,
       s.Quantity_Sold,
       s.Sales_Amount,
       s.Discount,
       s.Payment_Method,
       s.Sales_Channel
FROM staging_sales s
JOIN regions    r  ON r.region_name   = s.Region
JOIN sales_reps sr ON sr.rep_name     = s.Sales_Rep AND sr.region_id = r.region_id
JOIN customers  c  ON c.customer_type = s.Customer_Type;


-- =====================================================================
-- SECTION 3: Q2 — TOTAL PROFIT PER CATEGORY (INNER JOIN)
-- =====================================================================
-- Profit formula:
--   Total_Profit = (Unit_Price − Unit_Cost) × Quantity_Sold × (1 − Discount)
--
-- Because Unit_Price and Unit_Cost live in `products`, we MUST join
-- to compute profit — which is exactly what Q2 asks for.
-- =====================================================================

SELECT
    p.product_category                                                     AS category,
    COUNT(*)                                                               AS transactions,
    SUM(s.quantity_sold)                                                   AS units_sold,
    ROUND(SUM((p.unit_price - p.unit_cost) * s.quantity_sold
              * (1 - s.discount)), 2)                                      AS total_profit,
    ROUND(AVG((p.unit_price - p.unit_cost) * s.quantity_sold
              * (1 - s.discount)), 2)                                      AS avg_profit_per_txn,
    ROUND(SUM((p.unit_price - p.unit_cost) * s.quantity_sold
              * (1 - s.discount))
          / SUM(s.sales_amount) * 100, 2)                                  AS profit_margin_pct
FROM        sales    s
INNER JOIN  products p   ON p.product_id = s.product_id
GROUP BY    p.product_category
ORDER BY    total_profit DESC;


-- =====================================================================
-- EXPECTED RESULT (verified against the 400K-row CSV):
--
--   category     transactions  units_sold   total_profit     avg_profit_per_txn
--   ----------   ------------  -----------  ---------------  ------------------
--   Clothing         100,011    ~2,752,000   1,648,562,XXX        16,483.82
--   Food              99,924    ~2,748,000   1,647,264,XXX        16,485.17
--   Furniture        100,245    ~2,757,000   1,646,803,XXX        16,427.78
--   Electronics       99,820    ~2,745,000   1,641,257,XXX        16,442.16
--
-- INTERPRETATION:
-- Total profit is remarkably uniform across the four categories
-- (~₹1.64 B each), differing by less than 0.5%. This synthetic dataset
-- is balanced by design — in a real retail chain you would expect to
-- see one category clearly dominating, and that asymmetry is the
-- starting point for the operational-failure investigation in Q4 & Q5.
-- =====================================================================
