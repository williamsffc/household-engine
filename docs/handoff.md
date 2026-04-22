# Household Engine — Handoff / Current Repo Truth (Updated)

## Purpose of this document

This file is the **current repo truth / actual implemented state**.

It should describe:
- what is already built
- what routes/pages exist now
- what behavior is already real
- what is still missing
- what the next development slice should focus on

It should not be used as the long-term architecture blueprint.
For target design, use `architecture.md`.
For the immediate active step plan, use `Pasted_text.md`.

---

## Current status

Household Engine is currently:
- **V1-complete**
- plus **selective V2-ready hardening**
- local-first
- FastAPI + SQLite based
- usable through Overview, Expenses, and Review Queue pages

Step 13 is complete.

---

## What is implemented now

### Shared Hub

Implemented:
- FastAPI app shell
- SQLite database setup
- WAL mode
- migration runner
- document upload and registry
- process / reprocess support
- document metadata tracking
- file hashing
- audit logging
- processing runs support
- modest local-only middleware guardrail

### Expenses

Implemented:
- expense ingest pipeline
- parsers and categorization
- anomaly support
- expense repository logic
- expense routes
- monthly / categories / recent / summary read models
- Expenses UI page

Current user-facing state:
- backend works
- analytics work
- dashboard experience exists
- expense upload is still more backend-oriented than ideal from the UI perspective

### Payroll

Implemented:
- payroll tables and migrations
- payroll draft ingest pipeline
- native PDF extraction
- OCR fallback path
- PII scrubbing
- heuristic extraction / validation behavior
- draft persistence
- payroll ingest route
- payroll list/detail APIs
- monthly payroll aggregation API

Current user-facing state:
- payroll can be ingested into draft / in-review state
- payroll review payloads are visible
- approved payroll workflow does **not** exist yet

### Review Queue

Implemented:
- review queue backend
- review queue detail payloads
- Review Queue UI page
- display of metadata, redacted text, redaction counts, warnings, draft paystub, and draft lines

Current user-facing state:
- readable review surface exists
- it is still effectively read-only for payroll decisions

### Overview / analytics

Implemented:
- summary endpoint
- cashflow endpoint
- recent-documents endpoint
- trends endpoint
- forecast endpoint
- portfolio / deployable-surplus endpoint
- Overview UI page

Important current rule preserved:
- only approved payroll counts toward analytics
- current draft payroll contributes zero income

---

## Current implemented routes

### UI

- `GET /`
- `GET /expenses`
- `GET /review-queue`

### Overview API

- `GET /api/overview/summary`
- `GET /api/overview/recent-documents`
- `GET /api/overview/cashflow`
- `GET /api/overview/trends`
- `GET /api/overview/forecast`
- `GET /api/overview/portfolio`

### Expenses API

- `GET /api/expenses/transactions`
- `GET /api/expenses/monthly`
- `GET /api/expenses/categories`
- `GET /api/expenses/recent`
- `POST /api/expenses/documents/{document_id}/ingest`

### Payroll API

- `POST /api/payroll/documents/{document_id}/ingest`
- `GET /api/payroll/paystubs`
- `GET /api/payroll/paystubs/{paystub_id}`
- `GET /api/payroll/monthly`

### Review Queue API

- `GET /api/review-queue`
- `GET /api/review-queue/{document_id}`

---

## What is not implemented yet

### Payroll workflow gaps

Not implemented yet:
- payroll approve action
- payroll reject action
- canonical payroll approval flow
- approval-driven audit semantics
- dedicated Payroll page / paystub examination UI

### Review and extraction gaps

Not implemented yet:
- persisted review artifacts
- robust scanned-PDF OCR
- stronger payroll line-item extraction
- visual PDF redaction
- field-level extraction confidence

### Portfolio / broader V2 gaps

Not implemented yet:
- portfolio UI
- brokerage integrations
- richer allocation planning layer
- balance-aware surplus model
- richer auth / user-role system

---

## New immediate product/UI observations

The next iteration should acknowledge these UX realities:

1. **Upload should move into the UI**
   - users should interact through app pages rather than folder structure
   - Expenses should gain an in-page upload surface
   - Review Queue should gain an in-page payroll upload surface

2. **Navigation needs responsive behavior**
   - current navigation disappearing on smaller browser widths is a real UX issue
   - nav should collapse or transform, not vanish

3. **The current visual theme is too dark**
   - the next slice should introduce proper light/dark theme support instead of one-off color tweaks

4. **A dedicated Payroll page should follow, not lead**
   - first stabilize shell, theme, navigation, and upload UX
   - then add payroll approval workflow
   - then add Payroll page / paystub examination UI

---

## Recommended next build sequence

The next development slice should be:

1. **Theme system + shell foundation**
2. **Responsive navigation overhaul**
3. **Shared in-app upload component**
4. **Expenses UX refresh**
5. **Review Queue UX refresh**
6. **Payroll approval / canonical workflow**
7. **Dedicated Payroll page / paystub examination UI**

This sequencing fits the repo’s current state better than jumping immediately into the Payroll page.

---

## Current repo summary in one paragraph

The repo currently provides a working local-first Hub, a functioning Expenses module, a functioning payroll draft/review-oriented backend, a usable Review Queue UI, shared cashflow and forecasting outputs, and selective V2 hardening. The biggest remaining functional gap is payroll approval / canonicalization, while the biggest immediate UX gap is the shell itself: theme support, responsive navigation, and in-app upload flows.
