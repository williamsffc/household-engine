-- Step 4A: Expense analytics foundation
-- Create vw_monthly_expenses as a stable read model for monthly totals.
-- Idempotent via DROP VIEW IF EXISTS.

DROP VIEW IF EXISTS vw_monthly_expenses;

CREATE VIEW vw_monthly_expenses AS
SELECT
    substr(transaction_date, 1, 7) AS month,
    ROUND(SUM(amount), 2) AS total_expenses,
    COUNT(*) AS transaction_count
FROM expenses_transactions
GROUP BY substr(transaction_date, 1, 7);

