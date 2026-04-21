-- Expense tables (V1)

CREATE TABLE IF NOT EXISTS expenses_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    institution_id INTEGER,
    transaction_date TEXT NOT NULL,
    post_date TEXT,
    amount REAL NOT NULL,
    merchant_raw TEXT NOT NULL,
    merchant_normalized TEXT,
    category TEXT,
    subcategory TEXT,
    currency TEXT NOT NULL DEFAULT 'USD',
    fingerprint TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (institution_id) REFERENCES institutions(id)
);

CREATE INDEX IF NOT EXISTS idx_expenses_transactions_date
ON expenses_transactions(transaction_date);

CREATE INDEX IF NOT EXISTS idx_expenses_transactions_category
ON expenses_transactions(category);

CREATE INDEX IF NOT EXISTS idx_expenses_transactions_document
ON expenses_transactions(document_id);

CREATE INDEX IF NOT EXISTS idx_expenses_transactions_fingerprint
ON expenses_transactions(fingerprint);
