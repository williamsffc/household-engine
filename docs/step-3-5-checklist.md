# Household Engine — Step 3.5 Checklist

## Purpose
Step 3.5 is a short hardening pass after the successful Expense Recon backend migration.

The goal is to make the expense module stable and repeatable before moving into Step 4 (analytics / overview scaffolding).

This is **not** a new feature phase.
It is a **stability and validation phase**.

---

## Current Status Before Step 3.5
Completed:
- Step 1 — shared DB + migrations + FastAPI app shell
- Step 2 — upload flow + document registry
- Step 2.5 — bootstrap stabilization
- Step 3 — expense backend migration

Expense ingest is already working end-to-end:
- upload works with `module_owner = expenses`
- ingest works
- transactions are inserted into `expenses_transactions`
- listing transactions works

---

## Step 3.5 Goals
1. confirm supported expense file types work consistently
2. confirm re-ingest behavior is idempotent
3. confirm dependency setup is reproducible
4. confirm error handling is clean
5. confirm audit entries are written
6. avoid touching payroll, analytics, or frontend work yet

---

## Required Checks

### 1. Upload allowlist check
Confirm `src/api/routes_documents.py` allows all expense file types currently supported by `src/expenses/ingest.py`.

Expected allowed types:
- `.pdf`
- `.csv`
- `.txt`
- `.xlsx`
- `.xls`
- `.png`
- `.jpg`
- `.jpeg`

For expense ingestion specifically, the important ones are:
- `.pdf`
- `.csv`
- `.xlsx`
- `.xls`

#### Pass condition
Uploading supported expense source files does not fail due to extension allowlist mismatch.

---

### 2. Dependency check
Confirm `requirements.txt` includes all dependencies required by the expense module.

Expected minimum:
- `fastapi`
- `uvicorn[standard]`
- `python-multipart`
- `pandas`
- `pdfplumber`
- `pyyaml`
- `openpyxl`

#### Pass condition
A fresh environment can install dependencies and run the app without missing import errors for expense ingestion.

---

### 3. Expense ingest success check
Test one known-good expense source file end-to-end.

#### Test flow
1. upload a supported expense file through `/docs`
2. set `module_owner = expenses`
3. call `POST /api/expenses/documents/{document_id}/ingest`
4. verify success response
5. verify rows appear in `/api/expenses/transactions`

#### Pass condition
Expected ingest result:
- `ok: true`
- `inserted > 0`

---

### 4. CSV ingest check
Test one supported `.csv` expense file, if available.

#### Why
Step 3 already confirmed one successful expense ingest. This check ensures the module works for more than one supported format.

#### Pass condition
A valid CSV expense document uploads and ingests successfully.

---

### 5. Re-ingest idempotency check
Re-run ingest on the same expense document.

#### Why
`src/expenses/repository.py` deletes existing transactions for the same `document_id` before reinserting. This is intended to prevent duplicate rows.

#### Test flow
1. ingest a document once
2. record number of inserted rows
3. ingest the same document again
4. verify no duplicate accumulation for that `document_id`

#### Pass condition
Re-ingesting the same document does not duplicate rows.

---

### 6. Unsupported file error check
Upload or ingest a file that should not be supported by the expense pipeline.

Examples:
- unsupported extension
- valid extension but unsupported statement format

#### Pass condition
The API returns a clear, non-crashing error such as:
- unsupported file extension
- unrecognized statement format
- could not read file

---

### 7. Audit log verification
Confirm expense ingest writes audit log entries.

Expected events:
- expense ingest started
- expense ingest completed

Optional:
- confirm upload and document route audit entries also still exist

#### Pass condition
Expense-related actions are visible in `audit_log`.

---

### 8. Processing run verification
If the implementation records processing steps for expense ingestion, verify they are inserted consistently where intended.

This is optional if Step 3 did not add expense-specific processing run entries.

#### Pass condition
Either:
- processing runs are correctly written, or
- the current design intentionally limits them to document route stubs only

---

### 9. Transaction list endpoint sanity check
Test:
- `GET /api/expenses/transactions`
- optional filters such as:
  - `limit`
  - `category`
  - `institution_id`
  - `start_date`
  - `end_date`

#### Pass condition
The endpoint returns clean JSON and filter behavior is sane.

---

### 10. Optional API hardening
Optional but useful if easy:
- cap `limit` to a safe maximum
- add clearer error messages for malformed query params
- add typed Pydantic response models later

These are optional for Step 3.5 and should not block moving to Step 4.

---

## Explicit Non-Goals for Step 3.5
Do **not** implement:
- payroll ingestion
- payroll tables
- review queue business logic
- analytics views
- overview dashboard
- old expense dashboard frontend migration
- V2 features

---

## Recommended Manual Smoke Test Sequence

### A. Run the app
```powershell
cd household-engine
python -m pip install -r requirements.txt
python -m uvicorn src.main:app --reload