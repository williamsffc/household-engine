-- Step 5A: Payroll schema foundation (V1)
-- Idempotent: safe if 003_init_payroll.sql was an empty placeholder already applied.
-- Tables match architecture.md payroll storage model.

CREATE TABLE IF NOT EXISTS payroll_paystubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    institution_id INTEGER,
    status TEXT NOT NULL DEFAULT 'draft',
    pay_date TEXT NOT NULL,
    period_start TEXT,
    period_end TEXT,
    gross_pay REAL,
    net_pay REAL,
    currency TEXT NOT NULL DEFAULT 'USD',
    validation_summary TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (member_id) REFERENCES household_members(id),
    FOREIGN KEY (institution_id) REFERENCES institutions(id)
);

CREATE TABLE IF NOT EXISTS payroll_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paystub_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    ytd_amount REAL,
    display_order INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paystub_id) REFERENCES payroll_paystubs(id)
);

CREATE INDEX IF NOT EXISTS idx_payroll_paystubs_member
ON payroll_paystubs(member_id);

CREATE INDEX IF NOT EXISTS idx_payroll_paystubs_pay_date
ON payroll_paystubs(pay_date);

CREATE INDEX IF NOT EXISTS idx_payroll_lines_paystub
ON payroll_lines(paystub_id);

CREATE INDEX IF NOT EXISTS idx_payroll_lines_category
ON payroll_lines(category);
