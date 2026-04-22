-- Step 18: Persist payroll review artifacts (redacted text + metadata)
-- Makes Review Queue detail durable and faster (no regeneration on every read).

CREATE TABLE IF NOT EXISTS payroll_review_artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL UNIQUE,
    paystub_id INTEGER,
    redacted_text TEXT NOT NULL,
    redaction_counts_json TEXT NOT NULL,
    text_chars INTEGER,
    ocr_used_for_review INTEGER NOT NULL DEFAULT 0,
    source TEXT NOT NULL DEFAULT 'persisted',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (paystub_id) REFERENCES payroll_paystubs(id)
);

CREATE INDEX IF NOT EXISTS idx_payroll_review_artifacts_document
ON payroll_review_artifacts(document_id);

