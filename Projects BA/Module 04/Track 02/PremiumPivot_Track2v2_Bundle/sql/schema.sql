-- ============================================================================
-- Premium Pivot - Marketplace Schema (3NF)
-- For Track 2: Strategic Re-positioning of a Subscription Ecosystem
-- SQLite-compatible. 4 base tables + 5 analytical views.
-- ============================================================================

DROP TABLE IF EXISTS app_reviews;
DROP TABLE IF EXISTS app_categories;
DROP TABLE IF EXISTS apps;
DROP TABLE IF EXISTS price_buckets;

-- ---------- BASE TABLES ----------

CREATE TABLE price_buckets (
    bucket_id     INTEGER PRIMARY KEY,
    bucket_label  TEXT,
    price_min     REAL,
    price_max     REAL
);

CREATE TABLE app_categories (
    category      TEXT PRIMARY KEY,
    n_apps        INTEGER
);

CREATE TABLE apps (
    app_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    app_name      TEXT,
    category      TEXT,
    rating        REAL,
    n_reviews     INTEGER,
    size_mb       REAL,
    n_installs    INTEGER,
    is_paid       INTEGER,           -- 0=free, 1=paid
    price_usd     REAL,
    bucket_id     INTEGER,
    content_rating TEXT,
    last_updated  TEXT,
    FOREIGN KEY (category)   REFERENCES app_categories(category),
    FOREIGN KEY (bucket_id)  REFERENCES price_buckets(bucket_id)
);

CREATE TABLE app_reviews (
    review_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    app_name      TEXT,
    sentiment     TEXT,              -- Positive / Negative / Neutral
    polarity      REAL,
    subjectivity  REAL
);

CREATE INDEX idx_apps_cat       ON apps(category);
CREATE INDEX idx_apps_paid      ON apps(is_paid);
CREATE INDEX idx_apps_bucket    ON apps(bucket_id);
CREATE INDEX idx_revs_app       ON app_reviews(app_name);


-- ---------- ANALYTICAL VIEWS ----------

DROP VIEW IF EXISTS v_category_summary;
DROP VIEW IF EXISTS v_dupont_decomposition;
DROP VIEW IF EXISTS v_funnel_per_app;
DROP VIEW IF EXISTS v_price_band_summary;
DROP VIEW IF EXISTS v_app_with_sentiment;


-- 1. Category-level summary (denominator for the DuPont decomp)
CREATE VIEW v_category_summary AS
SELECT
    category,
    COUNT(*)                                              AS n_total_apps,
    SUM(is_paid)                                           AS n_paid_apps,
    SUM(n_installs)                                        AS total_installs,
    SUM(CASE WHEN is_paid=1 THEN n_installs ELSE 0 END)   AS paid_installs,
    SUM(CASE WHEN is_paid=1 THEN price_usd*n_installs ELSE 0 END) AS paid_gmv,
    AVG(CASE WHEN is_paid=1 THEN price_usd END)            AS avg_paid_price
FROM apps
GROUP BY category;


-- 2. DuPont-style decomposition by category
--    GMV  =  Total Installs  ×  Paid Install Rate  ×  Avg Paid Price
CREATE VIEW v_dupont_decomposition AS
SELECT
    category,
    n_total_apps,
    n_paid_apps,
    total_installs,
    paid_installs,
    paid_gmv,
    avg_paid_price,
    -- Decomposition components (the three "ratios")
    1.0 * total_installs                                                 AS comp1_total_installs,
    CASE WHEN total_installs > 0 THEN 1.0 * paid_installs/total_installs ELSE 0 END  AS comp2_paid_install_rate,
    avg_paid_price                                                       AS comp3_avg_paid_price
FROM v_category_summary
WHERE n_paid_apps >= 5;


-- 3. Per-app funnel (Install → Review → Advocate)
--    Advocacy = positive review proxy
CREATE VIEW v_funnel_per_app AS
SELECT
    a.app_id,
    a.app_name,
    a.category,
    a.is_paid,
    a.price_usd,
    a.n_installs,
    a.n_reviews,
    s.n_sentiment_reviews,
    s.pct_positive,
    s.pct_negative,
    -- Funnel rates
    CASE WHEN a.n_installs > 0 THEN 1.0 * a.n_reviews/a.n_installs ELSE 0 END   AS install_to_review_rate,
    CASE WHEN s.pct_positive IS NOT NULL THEN 1.0 * a.n_reviews * s.pct_positive ELSE NULL END AS advocate_count,
    CASE WHEN a.n_installs > 0 AND s.pct_positive IS NOT NULL
         THEN 1.0 * a.n_reviews * s.pct_positive / a.n_installs
         ELSE NULL
    END AS install_to_advocate_rate
FROM apps a
LEFT JOIN (
    SELECT app_name,
           COUNT(*)                                                    AS n_sentiment_reviews,
           1.0 * SUM(CASE WHEN sentiment='Positive' THEN 1 ELSE 0 END)/COUNT(*) AS pct_positive,
           1.0 * SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END)/COUNT(*) AS pct_negative
    FROM app_reviews
    GROUP BY app_name
) s ON a.app_name = s.app_name;


-- 4. Price-band summary (for price elasticity analysis)
CREATE VIEW v_price_band_summary AS
SELECT
    pb.bucket_id,
    pb.bucket_label,
    COUNT(a.app_id)                                  AS n_apps,
    AVG(a.price_usd)                                  AS mean_price,
    AVG(a.n_installs)                                 AS mean_installs,
    AVG(a.rating)                                     AS mean_rating,
    SUM(a.price_usd * a.n_installs)                   AS total_gmv
FROM price_buckets pb
LEFT JOIN apps a ON a.bucket_id = pb.bucket_id AND a.is_paid = 1
GROUP BY pb.bucket_id, pb.bucket_label
ORDER BY pb.bucket_id;


-- 5. Apps joined with sentiment summary (for STP segmentation work)
CREATE VIEW v_app_with_sentiment AS
SELECT
    a.*,
    s.n_sentiment_reviews,
    s.pct_positive,
    s.pct_negative,
    s.avg_polarity
FROM apps a
LEFT JOIN (
    SELECT app_name,
           COUNT(*)                                                    AS n_sentiment_reviews,
           1.0 * SUM(CASE WHEN sentiment='Positive' THEN 1 ELSE 0 END)/COUNT(*) AS pct_positive,
           1.0 * SUM(CASE WHEN sentiment='Negative' THEN 1 ELSE 0 END)/COUNT(*) AS pct_negative,
           AVG(polarity)                                              AS avg_polarity
    FROM app_reviews
    GROUP BY app_name
) s ON a.app_name = s.app_name;
