-- Persist recon metadata computed during ingest (flags, recurring, txn_type, account label).
-- Additive only; safe for existing household.db files. Keeps vw_monthly_expenses semantics
-- (still sums all rows in expenses_transactions, which remain outflow-only at insert time).

ALTER TABLE expenses_transactions ADD COLUMN is_flagged INTEGER NOT NULL DEFAULT 0;
ALTER TABLE expenses_transactions ADD COLUMN flag_reason TEXT;
ALTER TABLE expenses_transactions ADD COLUMN is_recurring INTEGER NOT NULL DEFAULT 0;
ALTER TABLE expenses_transactions ADD COLUMN txn_type TEXT NOT NULL DEFAULT 'expense';
ALTER TABLE expenses_transactions ADD COLUMN account_label TEXT;
