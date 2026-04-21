-- Step 7: Combined household cashflow view (approved-only income)
-- Combines vw_monthly_expenses (outflows) with approved payroll income.

DROP VIEW IF EXISTS vw_monthly_cashflow;

CREATE VIEW vw_monthly_cashflow AS
WITH expenses AS (
    SELECT
        month,
        ROUND(SUM(COALESCE(total_expenses, 0)), 2) AS total_expenses
    FROM vw_monthly_expenses
    GROUP BY month
),
income AS (
    SELECT
        month,
        ROUND(SUM(COALESCE(total_net_pay, 0)), 2) AS total_income
    FROM vw_monthly_payroll
    GROUP BY month
)
SELECT
    COALESCE(i.month, e.month) AS month,
    COALESCE(i.total_income, 0) AS total_income,
    COALESCE(e.total_expenses, 0) AS total_expenses,
    ROUND(COALESCE(i.total_income, 0) - COALESCE(e.total_expenses, 0), 2) AS net_cashflow
FROM income i
LEFT JOIN expenses e ON i.month = e.month

UNION

SELECT
    COALESCE(i.month, e.month) AS month,
    COALESCE(i.total_income, 0) AS total_income,
    COALESCE(e.total_expenses, 0) AS total_expenses,
    ROUND(COALESCE(i.total_income, 0) - COALESCE(e.total_expenses, 0), 2) AS net_cashflow
FROM expenses e
LEFT JOIN income i ON i.month = e.month
WHERE i.month IS NULL;

