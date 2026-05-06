-- =====================================================================
-- Question 1 — 2NF / 3NF Normalization of the Loan Dataset
-- Dataset: Bank Loan & Credit Risk
-- =====================================================================
--
-- Problem with the raw flat file (1NF only):
--   Each row mixes three different concerns:
--     - Borrower demographics (age, gender, education, income, ...)
--     - Credit history facts   (credit_score, cred_hist_length, ...)
--     - Loan transaction       (loan_amnt, loan_intent, loan_int_rate, ...)
--
--   If a borrower takes 3 loans, their demographics are repeated 3
--   times -> redundancy, update anomalies, wasted storage.
--
-- Normalization plan:
--   2NF: every non-key attribute depends on the WHOLE primary key.
--        Move borrower attributes (which depend only on borrower_id)
--        into a separate table.
--   3NF: no transitive dependencies. Move credit history into its own
--        table because it depends on borrower_id, not on loan_id.
--
-- Result: three tables linked by foreign keys.
--   borrowers       (PK: borrower_id)
--   credit_history  (PK: borrower_id  -> 1:1 with borrowers)
--   loans           (PK: loan_id, FK: borrower_id)
-- =====================================================================


-- ---------------------------------------------------------------------
-- DDL — create the three normalized tables
-- ---------------------------------------------------------------------
CREATE TABLE borrowers (
    borrower_id           INT          PRIMARY KEY,
    person_age            INT          NOT NULL,
    person_gender         VARCHAR(10),
    person_education      VARCHAR(20),
    person_income         DECIMAL(12,2),
    person_emp_exp        INT,
    person_home_ownership VARCHAR(15)
);

CREATE TABLE credit_history (
    borrower_id                    INT PRIMARY KEY,
    cb_person_cred_hist_length     DECIMAL(4,1),
    credit_score                   INT,
    previous_loan_defaults_on_file VARCHAR(3),
    FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
);

CREATE TABLE loans (
    loan_id              INT          PRIMARY KEY,
    borrower_id          INT          NOT NULL,
    loan_amnt            DECIMAL(12,2),
    loan_intent          VARCHAR(20),
    loan_int_rate        DECIMAL(5,2),
    loan_percent_income  DECIMAL(5,4),
    loan_status          INT,         -- 1 = default, 0 = current
    FOREIGN KEY (borrower_id) REFERENCES borrowers(borrower_id)
);


-- ---------------------------------------------------------------------
-- ETL — populate from the flat file (assumed loaded as `loan_data_raw`)
-- ---------------------------------------------------------------------
-- Step 1: borrowers (one row per unique borrower)
INSERT INTO borrowers (borrower_id, person_age, person_gender,
                       person_education, person_income, person_emp_exp,
                       person_home_ownership)
SELECT DISTINCT
    ROW_NUMBER() OVER (ORDER BY person_age, person_income) AS borrower_id,
    person_age, person_gender, person_education,
    person_income, person_emp_exp, person_home_ownership
FROM loan_data_raw;

-- Step 2: credit_history (one row per borrower)
INSERT INTO credit_history (borrower_id, cb_person_cred_hist_length,
                            credit_score, previous_loan_defaults_on_file)
SELECT
    b.borrower_id,
    r.cb_person_cred_hist_length,
    r.credit_score,
    r.previous_loan_defaults_on_file
FROM loan_data_raw r
JOIN borrowers b
  ON r.person_age            = b.person_age
 AND r.person_income         = b.person_income
 AND r.person_emp_exp        = b.person_emp_exp;

-- Step 3: loans (transactional — one row per loan)
INSERT INTO loans (loan_id, borrower_id, loan_amnt, loan_intent,
                   loan_int_rate, loan_percent_income, loan_status)
SELECT
    ROW_NUMBER() OVER (ORDER BY r.loan_amnt) AS loan_id,
    b.borrower_id,
    r.loan_amnt, r.loan_intent, r.loan_int_rate,
    r.loan_percent_income, r.loan_status
FROM loan_data_raw r
JOIN borrowers b
  ON r.person_age    = b.person_age
 AND r.person_income = b.person_income;


-- ---------------------------------------------------------------------
-- Sample analytical query against the normalized schema
-- ---------------------------------------------------------------------
-- "Average loan size by education level for borrowers under 30"
SELECT
    b.person_education,
    COUNT(l.loan_id)        AS loan_count,
    AVG(l.loan_amnt)        AS avg_loan_amount,
    AVG(c.credit_score)     AS avg_credit_score
FROM borrowers b
JOIN credit_history c ON b.borrower_id = c.borrower_id
JOIN loans         l ON b.borrower_id = l.borrower_id
WHERE b.person_age < 30
GROUP BY b.person_education
ORDER BY avg_loan_amount DESC;


-- =====================================================================
-- Why this design satisfies 2NF and 3NF
-- =====================================================================
-- 2NF: borrower attributes (age, gender, education, ...) no longer
--      live in the loans table — they only appear in the borrowers
--      table where they fully depend on the primary key (borrower_id).
--
-- 3NF: credit_score depends on borrower_id, not on loan_id. Moving it
--      to credit_history removes a transitive dependency (loan_id ->
--      borrower_id -> credit_score) from the loans table.
--
-- Benefits in production:
--   - Updating a borrower's email address touches one row, not many
--   - Storage shrinks roughly proportional to the avg loans-per-borrower
--   - Referential integrity prevents orphaned loans
-- =====================================================================
