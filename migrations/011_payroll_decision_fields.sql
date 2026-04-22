-- Step 18: Persist review decision traceability on paystubs.

ALTER TABLE payroll_paystubs ADD COLUMN decided_at TEXT;
ALTER TABLE payroll_paystubs ADD COLUMN decision_actor TEXT;
ALTER TABLE payroll_paystubs ADD COLUMN rejection_reason TEXT;

