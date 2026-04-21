-- Step 7: Payroll analytics view (approved-only)
-- Stable read model for monthly payroll totals.
-- IMPORTANT: Only approved payroll rows should contribute to household analytics.

DROP VIEW IF EXISTS vw_monthly_payroll;

CREATE VIEW vw_monthly_payroll AS
SELECT
    substr(pay_date, 1, 7) AS month,
    member_id,
    ROUND(SUM(COALESCE(net_pay, 0)), 2) AS total_net_pay,
    ROUND(SUM(COALESCE(gross_pay, 0)), 2) AS total_gross_pay,
    COUNT(*) AS paystub_count
FROM payroll_paystubs
WHERE status = 'approved'
GROUP BY substr(pay_date, 1, 7), member_id;

