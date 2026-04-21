Household Engine — Final Scope Summary
Core vision

A 100% local, privacy-first household financial platform with a Hub-and-Spoke architecture.

The Hub owns shared infrastructure:

local server
database
document intake
processing lifecycle
audit logging
review queue
app shell / navigation
shared analytics views

The Spokes own domain logic:

Expenses
Payroll
later Portfolio
much later, optional non-financial modules

The system is designed to answer:

what came in
what went out
what is pending review
what is recurring
what is changing over time
how much liquid surplus is actually available
Final V1 Goal

V1 is a local financial command center with two working modules:

Expenses
Payroll

And one shared cross-module outcome:

Household cashflow overview

V1 is not trying to be perfect document forensics, enterprise workflow software, or a life dashboard.

It is trying to be:

private
reliable
understandable
reviewable
modular
usable every week
What is included in V1
1. Core Hub platform
App framework
FastAPI backend
local-only deployment
simple local frontend using:
HTML
CSS
Vanilla JS
Chart.js
Shared platform responsibilities
app shell with sidebar navigation
upload endpoints
document registry
processing status tracking
review queue
audit log
shared DB access
analytics views
Sidebar / navigation for V1
Overview
Expenses
Payroll
Review Queue
2. Database for V1
Shared operational tables

These are platform-level tables.

household_members
institutions
documents
audit_log

Optional if easy in V1:

processing_runs
Suggested role of each
household_members

Tracks you and your spouse.

Fields likely include:

id
name or alias
role
institutions

Tracks the source of records.

Examples:

Chase
Amex
Employer name
payroll provider later if needed

Fields likely include:

id
name
type
documents

Tracks every uploaded source file.

Fields should include at least:

id
filename
file_hash
module_owner
status
upload_date
storage_path
mime_type
member_id nullable
institution_id nullable
ocr_used boolean
notes nullable
audit_log

Tracks important system and user actions.

Fields should include:

id
document_id nullable
actor
action
details
timestamp
3. Expense module in V1

This is the first functional spoke because you already have a strong base.

What gets built
migrate core logic from expense-recon
move parsing and business logic into src/expenses/
connect it to the Hub DB
write canonical expense rows into:
expenses_transactions
V1 expense capabilities
import statements / supported sources from your existing system
parse transactions
categorize transactions
identify basic anomalies already supported in your current app
store transactions in the main database
render expense dashboard views in the Expenses tab
V1 expense table
expenses_transactions

Likely fields:

id
document_id
date
amount
merchant
category_id or category
institution_id if needed

You can expand later, but V1 should stay aligned with the existing repo as much as possible.

4. Payroll module in V1

This is the second spoke and the main new build.

V1 payroll pipeline
upload paystub
register document
extract native PDF text with pdfplumber
use OCR only if native extraction fails or document is scanned
run layered PII scrubbing on extracted text
pass cleaned text to LLM for structured JSON extraction
run deterministic validation checks
send result to Review Queue
on approval, store payroll records
include approved records in analytics views
PII handling in V1

Use a layered approach:

regex
layout heuristics
presidio-analyzer
manual review in UI
Payroll storage model in V1

Use:

payroll_paystubs
payroll_lines

This is the agreed V1 simplification.

payroll_paystubs

Header-level fields:

id
document_id
member_id
institution_id
pay_date
start_date
end_date
gross_pay
net_pay
status optional
validation_summary optional
payroll_lines

Line-item rows:

id
paystub_id
category (earning, tax, deduction)
description
amount
ytd_amount
display_order optional
Payroll fields V1 should extract

Roughly 15–20 important fields, including:

pay date
pay period start/end
gross pay
net pay
regular earnings
overtime if present
bonus if present
tax lines
deduction lines
YTD values when available
5. Review Queue in V1

This is mandatory for payroll and useful for documents generally.

Purpose

No extracted payroll document should be treated as canonical immediately.

What the queue shows
uploaded document metadata
redacted extracted text
structured JSON output
validation warnings
approval / rejection controls
V1 review model

Instead of field-confidence scoring, use review flags like:

math check passed
required fields present
dates valid
YTD consistent
OCR fallback used
possible duplicate
manual review required

This is the agreed V1 replacement for fragile LLM “confidence scoring.”

6. Deterministic validation in V1

This is required.

Validation checks should include
gross vs taxes/deductions vs net consistency
required fields present
date sanity
period sanity
duplicate document hash check
YTD nondecreasing when comparable
warning on OCR fallback

Important: these are consistency checks, not proof of correctness.

7. Lifecycle states in V1

Use explicit document states.

Recommended V1 lifecycle:

uploaded
processing
in_review
approved
rejected
error

If you want more granularity, later you can split processing into:

text_extracted
redacted
structured_extracted

But the simpler state model is enough for V1.

8. Analytics layer in V1

Use SQLite views, not complex dashboard-side business logic.

Required V1 read models

At minimum:

vw_monthly_cashflow

Optional if easy:

vw_monthly_expenses
vw_monthly_payroll
vw_household_cashflow
Purpose

The UI should read from stable views, not directly from ingestion tables.

That keeps:

dashboards cleaner
module boundaries healthier
future schema changes easier
9. Overview dashboard in V1
What it should answer
recent income
recent expenses
month-to-date net cashflow
pending review items
basic household trend
What it should not try to answer yet
sophisticated portfolio optimization
tax forecasting by jurisdiction
advanced budgeting simulation
wellness correlation
What is explicitly pushed to V2

These are intentionally deferred.

1. Visual PDF redaction

Not in V1.

Why deferred
PDF coordinate mapping
bbox rendering
flattening black boxes into export-safe PDFs
significant debugging burden
V1 alternative
keep original PDFs local in secure raw storage
only show redacted text in UI
do not produce a visually blacked-out PDF yet
2. Field-level confidence scoring

Not in V1.

Why deferred
LLM self-scoring is unreliable
fake confidence numbers are misleading
deterministic validation + review queue is better for V1
V1 alternative

Use document-level flags and validation warnings.

3. Portfolio module

Deferred to V2.

Why deferred

Portfolio is valuable, but should come after:

expenses are stable
payroll is stable
household cashflow is trustworthy
V2 goal

Read approved payroll + expense outputs to estimate deployable surplus.

4. Wellness / non-financial tracking

Deferred beyond V2 unless priorities change.

Why deferred

It breaks focus and adds a different data model.
V1 should stay a financial command center.

5. More advanced multi-user/local-network hardening

Probably V2.

Examples:

richer auth
stronger user roles
advanced local network access controls
more complex sync patterns

For V1, local-first single-household usage is enough.

6. Advanced payroll intelligence

Deferred to V2.

Examples:

employer-specific parsers
per-field confidence scoring
richer anomaly scoring
smarter line classification
advanced tax trend forecasting
direct visual paystub annotation
Development phases
Phase 0 — Prep and design freeze

Goal: lock the build target before coding.

Deliverables
final V1 scope agreed
repo strategy agreed
naming conventions agreed
tech stack frozen
database schema draft approved
folder structure draft approved
Output

A stable blueprint to hand to your coding workflow.

Phase 1 — Build the Core Hub

Goal: create the empty house.

Build
initialize FastAPI app
create project structure
create SQLite database
enable WAL mode
add shared tables
build app shell and sidebar
create upload endpoints
create document registry
create audit logging basics
create review queue shell
define lifecycle status handling
Done when

You can run the app locally, upload a document, and see it registered in the system.

Phase 2 — Integrate Expense Recon

Goal: make the first spoke live.

Build
migrate your existing expense logic into src/expenses/
connect it to the master DB
adapt transaction writes to expenses_transactions
mount existing expense dashboard into Expenses tab
confirm imports work under the Hub
verify categories and anomaly logic survive migration
Done when

The Expenses tab works end-to-end inside the new Hub.

Phase 3 — Build Payroll Engine

Goal: create the second spoke.

Build
create src/payroll/
implement PDF text extraction
add OCR fallback
implement layered PII scrubber
define LLM extraction schema
implement structured JSON extraction
build deterministic validation rules
store extracted draft data
route results to Review Queue
approve/reject flow writes canonical payroll rows
Done when

A paystub can be uploaded, sanitized, reviewed, approved, and stored.

Phase 4 — Build Shared Analytics / Overview

Goal: make the system feel like one command center.

Build
create analytics views
build Overview dashboard
show monthly income vs expenses
show pending review items
show household cashflow summary
clean up navigation and presentation
Done when

You can open the Overview tab and understand household financial movement at a glance.

Phase 5 — Stabilization and hardening

Goal: make V1 reliable enough for normal ongoing use.

Build
duplicate handling improvements
error handling improvements
better audit detail
test with multiple real documents
refine payroll prompts
refine PII rules
refine review warnings
improve import resilience
Done when

You trust it with regular real-world use.

V1 development order inside each area
Core Hub order
FastAPI bootstrap
SQLite initialization
shared schema
upload endpoint
document registry
app shell
review queue shell
status model
audit logging
Expense order
port parser code
port categorization logic
connect DB writes
connect dashboard tab
verify imports
verify anomalies
Payroll order
file intake
native text extraction
OCR fallback
PII scrubber
LLM extraction schema
validation rules
draft storage
review queue
approval flow
analytics inclusion
Analytics order
monthly expense view
monthly payroll view
combined cashflow view
overview dashboard cards
trend charts
V1 success criteria

V1 is successful if all of this is true:

runs fully locally
raw sensitive documents stay local
expenses module works inside the Hub
payroll paystubs can be uploaded and processed
PII is scrubbed before LLM extraction
payroll outputs require approval before becoming canonical
dashboards read from stable analytics views
overview shows meaningful household cashflow
system is modular enough to add portfolio later without redesign
Final V1 / V2 split
V1 includes
FastAPI Hub
shared local DB
document registry
audit log
review queue
expenses spoke
payroll spoke
layered PII text scrubbing
native PDF extraction + OCR fallback
deterministic validation
analytics views
overview dashboard
household cashflow summary
V2 includes
visual PDF redaction
field-level confidence scoring
portfolio spoke
deeper payroll forecasting
richer anomaly detection
stronger auth / advanced local networking
more advanced provider abstraction and parser sophistication
optional wellness or non-financial modules
One-line summary

V1 is a local, privacy-first household financial command center with a shared Hub, an integrated expense module, a review-driven payroll module, and unified household cashflow analytics; V2 adds visual redaction, richer intelligence, and portfolio expansion.

Household Engine — V1 Repo Tree

household-engine/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── run.py
├── household.db                 # local SQLite database (created at runtime)
├── data/
│   ├── raw/                     # original uploaded files, local only
│   ├── staging/                 # temporary processing artifacts
│   ├── processed/               # approved/finished artifacts if needed
│   ├── rejected/                # rejected docs
│   └── exports/                 # CSV, JSON, reports
├── config/
│   ├── app.yaml
│   ├── institutions.yaml
│   ├── expense_categories.yaml
│   ├── pii_patterns.yaml
│   └── payroll_schema.yaml
├── migrations/
│   ├── 001_init_shared.sql
│   ├── 002_init_expenses.sql
│   ├── 003_init_payroll.sql
│   └── 004_init_views.sql
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── settings.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   ├── file_store.py
│   │   ├── hashing.py
│   │   ├── statuses.py
│   │   └── exceptions.py
│   ├── api/
│   │   ├── routes_health.py
│   │   ├── routes_documents.py
│   │   ├── routes_review.py
│   │   ├── routes_overview.py
│   │   ├── routes_expenses.py
│   │   └── routes_payroll.py
│   ├── models/
│   │   ├── shared.py
│   │   ├── expense.py
│   │   └── payroll.py
│   ├── schemas/
│   │   ├── shared.py
│   │   ├── expense.py
│   │   └── payroll.py
│   ├── services/
│   │   ├── documents.py
│   │   ├── review_queue.py
│   │   ├── audit.py
│   │   ├── analytics.py
│   │   └── llm_client.py
│   ├── expenses/
│   │   ├── ingest.py
│   │   ├── parsers/
│   │   │   ├── chase.py
│   │   │   ├── amex.py
│   │   │   └── common.py
│   │   ├── categorizer.py
│   │   ├── anomalies.py
│   │   ├── repository.py
│   │   └── views.py
│   ├── payroll/
│   │   ├── ingest.py
│   │   ├── extractor_pdf.py
│   │   ├── extractor_ocr.py
│   │   ├── pii_scrubber.py
│   │   ├── validator.py
│   │   ├── normalizer.py
│   │   ├── repository.py
│   │   └── views.py
│   └── templates/
│       ├── base.html
│       ├── overview.html
│       ├── expenses.html
│       ├── payroll.html
│       └── review_queue.html
├── static/
│   ├── css/
│   │   └── app.css
│   ├── js/
│   │   ├── app.js
│   │   ├── overview.js
│   │   ├── expenses.js
│   │   ├── payroll.js
│   │   └── review_queue.js
│   └── vendor/
│       └── chart.min.js
└── tests/
    ├── test_documents.py
    ├── test_expenses.py
    ├── test_payroll_validation.py
    └── test_views.py

Repo responsibilities by folder
src/core/

Shared infrastructure only:

DB connection
settings
storage paths
lifecycle/status constants
hashing
error handling
src/api/

FastAPI endpoints only:

thin route handlers
request/response models
delegate to services/modules
src/services/

Cross-module platform services:

document registry
audit log writing
review queue operations
analytics orchestration
LLM provider wrapper
src/expenses/

Expense-only domain logic:

importers
parsers
categorization
anomalies
expense data access
src/payroll/

Payroll-only domain logic:

text extraction
OCR fallback
PII scrub
structured normalization
validation
payroll data access
migrations/

Raw SQL schema migrations.
Keep them simple and explicit.

SQLite V1 schema

Below is the V1 schema I recommend.

1. Shared operational tables
household_members
CREATE TABLE household_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL,              -- e.g. self, spouse
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
institutions
CREATE TABLE institutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL,              -- e.g. bank, card_issuer, employer, payroll_provider
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
documents
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    module_owner TEXT NOT NULL,      -- expenses, payroll
    status TEXT NOT NULL,            -- uploaded, processing, in_review, approved, rejected, error
    file_hash TEXT NOT NULL UNIQUE,
    mime_type TEXT,
    storage_path TEXT NOT NULL,
    member_id INTEGER,
    institution_id INTEGER,
    ocr_used INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    uploaded_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES household_members(id),
    FOREIGN KEY (institution_id) REFERENCES institutions(id)
);
audit_log
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    actor TEXT NOT NULL,             -- system, user
    action TEXT NOT NULL,            -- uploaded, parsed, scrubbed, approved, rejected, etc.
    details TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
Optional but useful: processing_runs
CREATE TABLE processing_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    module_owner TEXT NOT NULL,
    stage TEXT NOT NULL,             -- extract_text, scrub_pii, llm_extract, validate
    outcome TEXT NOT NULL,           -- success, warning, failed
    message TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES documents(id)
);
2. Expense tables
expenses_transactions
CREATE TABLE expenses_transactions (
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

Recommended indexes:

CREATE INDEX idx_expenses_transactions_date
ON expenses_transactions(transaction_date);

CREATE INDEX idx_expenses_transactions_category
ON expenses_transactions(category);

CREATE INDEX idx_expenses_transactions_document
ON expenses_transactions(document_id);

CREATE INDEX idx_expenses_transactions_fingerprint
ON expenses_transactions(fingerprint);
3. Payroll tables
payroll_paystubs

This is the paystub header.

CREATE TABLE payroll_paystubs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    institution_id INTEGER,
    status TEXT NOT NULL DEFAULT 'draft',  -- draft, approved, rejected
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
payroll_lines

This is the normalized line-item table.

CREATE TABLE payroll_lines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    paystub_id INTEGER NOT NULL,
    category TEXT NOT NULL,          -- earning, tax, deduction
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    ytd_amount REAL,
    display_order INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paystub_id) REFERENCES payroll_paystubs(id)
);

Recommended indexes:

CREATE INDEX idx_payroll_paystubs_member
ON payroll_paystubs(member_id);

CREATE INDEX idx_payroll_paystubs_pay_date
ON payroll_paystubs(pay_date);

CREATE INDEX idx_payroll_lines_paystub
ON payroll_lines(paystub_id);

CREATE INDEX idx_payroll_lines_category
ON payroll_lines(category);
Document lifecycle for V1

Use these statuses consistently.

documents.status
uploaded
processing
in_review
approved
rejected
error
payroll_paystubs.status
draft
approved
rejected

That gives you enough structure without overcomplicating V1.

Analytics views for V1

These should power the UI instead of querying raw ingestion tables directly.

1. Monthly expenses view
CREATE VIEW vw_monthly_expenses AS
SELECT
    substr(transaction_date, 1, 7) AS month,
    ROUND(SUM(amount), 2) AS total_expenses,
    COUNT(*) AS transaction_count
FROM expenses_transactions
GROUP BY substr(transaction_date, 1, 7);
2. Monthly payroll view
CREATE VIEW vw_monthly_payroll AS
SELECT
    substr(pay_date, 1, 7) AS month,
    member_id,
    ROUND(SUM(net_pay), 2) AS total_net_pay,
    ROUND(SUM(gross_pay), 2) AS total_gross_pay,
    COUNT(*) AS paystub_count
FROM payroll_paystubs
WHERE status = 'approved'
GROUP BY substr(pay_date, 1, 7), member_id;
3. Combined household cashflow
CREATE VIEW vw_monthly_cashflow AS
WITH expenses AS (
    SELECT
        substr(transaction_date, 1, 7) AS month,
        ROUND(SUM(amount), 2) AS total_expenses
    FROM expenses_transactions
    GROUP BY substr(transaction_date, 1, 7)
),
income AS (
    SELECT
        substr(pay_date, 1, 7) AS month,
        ROUND(SUM(net_pay), 2) AS total_income
    FROM payroll_paystubs
    WHERE status = 'approved'
    GROUP BY substr(pay_date, 1, 7)
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
4. Review queue view
CREATE VIEW vw_review_queue AS
SELECT
    d.id AS document_id,
    d.module_owner,
    d.original_filename,
    d.status,
    d.uploaded_at,
    d.ocr_used,
    d.notes
FROM documents d
WHERE d.status = 'in_review'
ORDER BY d.uploaded_at DESC;
FastAPI endpoint map for V1
Health / app
GET /health

Basic health check.

Response:

{ "status": "ok" }
GET /

Serve the Overview page.

Documents / uploads
POST /api/documents/upload

Upload a file and register it in documents.

Form fields:

file
module_owner (expenses or payroll)
member_id optional
institution_id optional

Response:

{
  "document_id": 12,
  "status": "uploaded",
  "module_owner": "payroll"
}
GET /api/documents

List documents with filters.

Query params:

module_owner
status
member_id
GET /api/documents/{document_id}

Return metadata for one document.

POST /api/documents/{document_id}/process

Start processing for the module owner.

expenses: parse/import
payroll: extract/scrub/structure/validate
POST /api/documents/{document_id}/reprocess

Retry processing after a failure.

Review queue
GET /api/review-queue

Return pending review items.

GET /api/review-queue/{document_id}

Return review payload for one document.

For payroll this should include:

document metadata
redacted text
structured extracted JSON
validation warnings
draft paystub header
draft payroll lines
POST /api/review-queue/{document_id}/approve

Approve draft output and mark as canonical.

For payroll:

set documents.status = approved
set payroll_paystubs.status = approved
POST /api/review-queue/{document_id}/reject

Reject the extracted result.

Body:

{
  "reason": "gross pay mismatched source"
}
Overview / analytics
GET /api/overview/summary

Return dashboard cards.

Suggested response:

{
  "month": "2026-04",
  "total_income": 11250.00,
  "total_expenses": 6840.22,
  "net_cashflow": 4409.78,
  "pending_reviews": 2
}
GET /api/overview/cashflow

Return rows from vw_monthly_cashflow.

GET /api/overview/recent-documents

Return recent uploads and statuses.

Expenses
GET /api/expenses/transactions

List expense transactions.

Filters:

start_date
end_date
category
institution_id
GET /api/expenses/monthly

Return rows from vw_monthly_expenses.

GET /api/expenses/categories

Return category breakdown.

POST /api/expenses/documents/{document_id}/ingest

Explicitly ingest an expense document if needed.

Payroll
GET /api/payroll/paystubs

List payroll paystubs.

Filters:

member_id
start_date
end_date
status
GET /api/payroll/paystubs/{paystub_id}

Return paystub header + lines.

GET /api/payroll/monthly

Return monthly payroll aggregates.

GET /api/payroll/members/{member_id}/trend

Return member-level payroll trend.

POST /api/payroll/documents/{document_id}/ingest

Explicit payroll processing route if you want module-specific control.

Recommended processing flow by module
Expense processing flow
upload file
create documents row
set status to processing
parse statement
write expenses_transactions
set document to approved
write audit log entries
Payroll processing flow
upload file
create documents row
set status to processing
native PDF text extraction
OCR fallback if needed
layered PII scrub
LLM structured extraction
deterministic validation
write draft payroll_paystubs + payroll_lines
set document to in_review
user approves or rejects
approved rows included in analytics
Suggested Pydantic schema groups
Shared
DocumentCreateResponse
DocumentDetail
ReviewQueueItem
AuditLogEntry
Expenses
ExpenseTransaction
ExpenseMonthlySummary
Payroll
PayrollLine
PayrollPaystubDraft
PayrollPaystubApproved
PayrollReviewPayload
PayrollValidationResult
V1 route ownership by file
routes_documents.py
upload
list documents
get document
process/reprocess
routes_review.py
review queue list
review payload detail
approve
reject
routes_overview.py
dashboard summary
cashflow chart
recent documents
routes_expenses.py
expense transactions
expense monthly summaries
category summaries
routes_payroll.py
payroll paystub list/detail
payroll monthly summaries
payroll member trends
Recommended first migrations order
001_init_shared.sql

Create:

household_members
institutions
documents
audit_log
processing_runs
002_init_expenses.sql

Create:

expenses_transactions
indexes
003_init_payroll.sql

Create:

payroll_paystubs
payroll_lines
indexes
004_init_views.sql

Create:

vw_monthly_expenses
vw_monthly_payroll
vw_monthly_cashflow
vw_review_queue
Recommended V1 bootstrap sequence
Step 1

Create shared DB + migrations + FastAPI app shell.

Step 2

Implement upload flow and document registry.

Step 3

Port expense-recon into src/expenses/.

Step 4

Make expense dashboard work under the Hub.

Step 5

Build payroll extraction pipeline.

Step 6

Build review queue approval flow.

Step 7

Build overview analytics.

Step 8

Harden with real sample docs.

Final practical recommendation

For V1, keep the code rule simple:

shared platform logic lives in core/, services/, api/
expense logic lives only in expenses/
payroll logic lives only in payroll/
dashboard reads views, not raw tables
only approved payroll records affect household analytics

If you want, next I can turn this into:

the actual SQL migration files, or
a FastAPI starter skeleton with route stubs and model files.

### Step 1–2 Acceptance Criteria
- app starts with `uvicorn src.main:app --reload`
- `/health` returns 200 and `{ "status": "ok" }`
- upload writes file to `data/raw/`
- upload inserts a document row into SQLite
- listing documents returns uploaded row
- fetching single document by ID works
- process/reprocess endpoints exist and return placeholder success
- rerunning startup does not duplicate migration side effects