-- UPI / Fintech Transaction Analysis (MySQL 8+)
-- Demo data only: all records are synthetic. A flag is not proof of fraud.

CREATE DATABASE IF NOT EXISTS upi_analytics;
USE upi_analytics;

-- If importing data with MySQL Workbench Table Data Import Wizard,
-- create the table first, then import data/upi_transactions.csv.
CREATE TABLE IF NOT EXISTS upi_transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    `timestamp` DATETIME,
    customer_id VARCHAR(20),
    amount_inr DECIMAL(12,2),
    payment_method VARCHAR(20),
    merchant_category VARCHAR(40),
    transaction_status VARCHAR(20),
    device_type VARCHAR(20),
    city VARCHAR(40),
    is_flagged TINYINT
);

-- 1. Basic dataset overview
SELECT COUNT(*) AS total_transactions,
       ROUND(SUM(amount_inr), 2) AS total_transaction_value_inr,
       ROUND(AVG(amount_inr), 2) AS average_transaction_amount_inr
FROM upi_transactions;

-- 2. Transaction volume and value by status
SELECT transaction_status,
       COUNT(*) AS transaction_count,
       ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM upi_transactions
GROUP BY transaction_status
ORDER BY transaction_count DESC;

-- 3. Hour-of-day analysis
SELECT HOUR(`timestamp`) AS transaction_hour,
       COUNT(*) AS transaction_count,
       ROUND(AVG(amount_inr), 2) AS average_amount_inr
FROM upi_transactions
GROUP BY HOUR(`timestamp`)
ORDER BY transaction_hour;

-- 4. Payment method summary
SELECT payment_method,
       COUNT(*) AS transaction_count,
       ROUND(SUM(amount_inr), 2) AS total_amount_inr
FROM upi_transactions
GROUP BY payment_method
ORDER BY total_amount_inr DESC;

-- 5. Rule-based flags by hour (review queue only, not confirmed fraud)
SELECT HOUR(`timestamp`) AS transaction_hour,
       COUNT(*) AS flagged_count,
       ROUND(AVG(amount_inr), 2) AS average_flagged_amount_inr
FROM upi_transactions
WHERE is_flagged = 1
GROUP BY HOUR(`timestamp`)
ORDER BY flagged_count DESC;

-- 6. Flagged rate by transaction status
SELECT transaction_status,
       COUNT(*) AS total_count,
       SUM(is_flagged) AS flagged_count,
       ROUND(100.0 * SUM(is_flagged) / COUNT(*), 2) AS flagged_percentage
FROM upi_transactions
GROUP BY transaction_status;
