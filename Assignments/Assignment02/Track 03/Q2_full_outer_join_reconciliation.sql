-- =====================================================================
-- Question 2 — FULL OUTER JOIN: Reconcile Applications vs Funded Loans
-- Dataset: Bank Loan & Credit Risk (45,000 records)
-- =====================================================================
--
-- Business context:
--   The Risk Committee needs to reconcile two operational systems:
--     - applications  : every loan request that was submitted
--     - funded_loans  : every loan that was actually disbursed
--
--   In a healthy pipeline these should agree on application_id.
--   In practice they often don't:
--     - Some applications are approved but never funded (borrower
--       withdraws, declines terms, or fails final verification)
--     - Some disbursements are missing from the application register
--       (data entry errors, system migration gaps)
--
--   A FULL OUTER JOIN surfaces both sides of the discrepancy in
--   one query — this is the canonical reconciliation pattern.
--
-- Setup (run once in Python before this query):
--   df['application_id'] = ['APP-' + str(i).zfill(6) for i in range(len(df))]
--   applications = df.sample(frac=0.99, random_state=1)  -> 44,550 rows
--   funded_loans = df.sample(frac=0.90, random_state=2)  -> 40,500 rows
-- =====================================================================


-- ---------------------------------------------------------------------
-- ANSI / Standard SQL  (works in PostgreSQL, SQL Server, Snowflake,
-- BigQuery, Oracle)
-- ---------------------------------------------------------------------
SELECT
    COALESCE(a.application_id, f.application_id) AS application_id,
    a.loan_amnt           AS requested_amount,
    f.loan_amnt           AS funded_amount,
    CASE
        WHEN a.application_id IS NULL THEN 'FUNDED_NO_APPLICATION'
        WHEN f.application_id IS NULL THEN 'APPLIED_NOT_FUNDED'
        ELSE 'MATCHED'
    END                   AS reconciliation_status
FROM applications a
FULL OUTER JOIN funded_loans f
    ON a.application_id = f.application_id
WHERE a.application_id IS NULL          -- only in funded
   OR f.application_id IS NULL          -- only in applications
ORDER BY reconciliation_status, application_id;


-- ---------------------------------------------------------------------
-- Executive summary — counts on each side of the discrepancy
-- ---------------------------------------------------------------------
SELECT
    CASE
        WHEN a.application_id IS NULL THEN 'FUNDED_NO_APPLICATION'
        WHEN f.application_id IS NULL THEN 'APPLIED_NOT_FUNDED'
        ELSE 'MATCHED'
    END AS reconciliation_status,
    COUNT(*) AS record_count
FROM applications a
FULL OUTER JOIN funded_loans f
    ON a.application_id = f.application_id
GROUP BY
    CASE
        WHEN a.application_id IS NULL THEN 'FUNDED_NO_APPLICATION'
        WHEN f.application_id IS NULL THEN 'APPLIED_NOT_FUNDED'
        ELSE 'MATCHED'
    END
ORDER BY record_count DESC;


-- ---------------------------------------------------------------------
-- MySQL workaround (MySQL does not support FULL OUTER JOIN natively)
-- Use UNION of LEFT JOIN + RIGHT JOIN
-- ---------------------------------------------------------------------
-- SELECT a.application_id AS app_id, f.application_id AS fund_id
-- FROM applications a
-- LEFT JOIN funded_loans f ON a.application_id = f.application_id
-- WHERE f.application_id IS NULL
-- UNION
-- SELECT a.application_id AS app_id, f.application_id AS fund_id
-- FROM applications a
-- RIGHT JOIN funded_loans f ON a.application_id = f.application_id
-- WHERE a.application_id IS NULL;


-- ---------------------------------------------------------------------
-- SQLite workaround (SQLite versions <3.39 also lack FULL OUTER JOIN)
-- Same UNION pattern works
-- ---------------------------------------------------------------------


-- =====================================================================
-- Result against the dataset
-- =====================================================================
-- reconciliation_status   | record_count
-- ------------------------+-------------
-- MATCHED                 |   40,092
-- APPLIED_NOT_FUNDED      |    4,458   <- 10% drop-off rate (approval-to-funding)
-- FUNDED_NO_APPLICATION   |      408   <- DATA QUALITY RED FLAG
--
-- Risk Committee implications:
--   1. The 4,458 APPLIED_NOT_FUNDED rows are a normal funnel leak —
--      worth analyzing to find why borrowers walk away (rate too high?
--      KYC failures? competitor poached?).
--   2. The 408 FUNDED_NO_APPLICATION rows are a control failure.
--      Loans were disbursed without a matching application record.
--      Audit and compliance should investigate immediately — this
--      could indicate process workarounds or data integrity issues.
-- =====================================================================
