# Household Engine — Handoff / Current Repo Truth

## Project state

Completed:

* Step 1
* Step 2
* Step 2.5
* Step 3
* Step 3.5
* Step 4A
* Step 4B
* Step 5A
* Step 5B
* Step 5C
* Step 6
* Step 7
* Step 8
* Step 9
* Step 10
* Step 11
* Step 12
* Step 13
* Step 14A
* Step 14B
* Step 14C
* Step 14D
* Step 14E

Current active step:

* Step 15 — Payroll Approval / Canonical Workflow

## Current status

Household Engine is now:

* V1-complete
* plus selective V2-ready hardening
* plus UI foundation refresh completed enough to support next workflow work

## What is working now

### Core platform

* local-first FastAPI Hub
* shared SQLite database and migrations
* upload flow and document registry
* processing runs and audit logging
* modest local-only network guardrail

### Expenses

* expense ingest pipeline
* parser/repository logic
* categorization and anomalies
* expenses analytics endpoints
* Expenses UI page
* in-app Expenses upload surface
* upload-to-ingest wiring in current frontend flow
* labeled upload entry point on page
* partial-failure banner behavior instead of all-or-nothing page failure
* calmer loading placeholders
* safer chart re-rendering
* improved phone-width summary-card layout

### Payroll / review

* payroll draft ingest pipeline
* payroll paystub APIs
* review queue backend
* Review Queue UI page
* payroll draft review payloads
* in-app Review Queue payroll upload surface
* clearer upload hierarchy and `in_review` explanation
* more scannable selected-item detail layout
* calmer loading states and partial-failure behavior

### Shared analytics / overview

* cashflow analytics views
* overview dashboard UI
* trend / forecast endpoints
* portfolio / deployable-surplus endpoint

### Shared shell / UI foundation

* shared base shell across current UI pages
* semantic theme token system in shared CSS
* light mode default
* dark mode support
* theme toggle in shared shell
* theme preference persisted locally
* early theme initialization to reduce flash on load
* Overview / Expenses chart styling updated to use theme-driven variables
* shell/theme cleanup for hover, active-row, overlay, focus-visible, callout, codeblock, and banner/error token states

### Responsive shell behavior

* topbar is now shared across current UI pages
* large screens use full sidebar with icons + labels
* medium screens use collapsed icon rail
* small screens use menu button + off-canvas drawer + backdrop
* drawer state is handled with small explicit shared JS
* nav no longer disappears on smaller widths
* cache-busted shared shell CSS/JS asset URLs added in base template to avoid stale browser assets
* responsive shell behavior is browser-validated

### Shared upload interaction layer

* shared upload surface helper exists in shared JS
* upload surface is reusable across pages
* drag-and-drop + click-to-upload supported
* upload states include idle, drag-over, uploading, success, and error
* current upload integration uses existing `POST /api/documents/upload`
* Review Queue payroll upload currently uses manual `member_id` entry

## Current implemented routes

### UI

* `GET /`
* `GET /expenses`
* `GET /review-queue`

### Overview API

* `GET /api/overview/summary`
* `GET /api/overview/recent-documents`
* `GET /api/overview/cashflow`
* `GET /api/overview/trends`
* `GET /api/overview/forecast`
* `GET /api/overview/portfolio`

### Expenses API

* `GET /api/expenses/transactions`
* `GET /api/expenses/monthly`
* `GET /api/expenses/categories`
* `GET /api/expenses/recent`
* `POST /api/expenses/documents/{document_id}/ingest`

### Payroll API

* `POST /api/payroll/documents/{document_id}/ingest`
* `GET /api/payroll/paystubs`
* `GET /api/payroll/paystubs/{paystub_id}`
* `GET /api/payroll/monthly`

### Review Queue API

* `GET /api/review-queue`
* `GET /api/review-queue/{document_id}`

## Product rule now locked in

The app is **household-first**, but every payroll record belongs to exactly **one household member**.

This means:

* payroll should be tracked per member
* approved payroll analytics should support both:
  * per-member views
  * household combined rollups
* household payroll totals should be computed from approved per-member payroll

This is the intended model for Person-M and Person-W going forward.

## What is not implemented yet

### Payroll / canonicalization

* no approve/reject payroll workflow yet
* no canonical payroll approval flow yet
* no dedicated Payroll page / paystub examination UI yet
* no robust scanned-PDF OCR yet
* no strong payroll line-item extraction yet

### Review queue / artifact persistence

* no approve endpoint yet
* no reject endpoint yet
* no persisted redacted review artifact yet

### Payroll member UX

* Review Queue payroll upload still needs a better member-selection UX
* dedicated member-level payroll browsing/filtering UI does not exist yet
* household vs per-member payroll views are not yet surfaced in UI

### Portfolio / later V2

* no portfolio UI yet
* no brokerage integrations
* no richer allocation planning layer
* no balance-aware surplus model

### Deferred advanced items

* no visual PDF redaction
* no field-level extraction confidence
* no full auth / user-role system
* no broader advanced anomaly scoring yet

## Immediate recommended next work

Proceed with:

* Step 15 — Payroll Approval / Canonical Workflow

Then:

* Step 16 — Dedicated Payroll page / paystub examination UI
* Step 17 — Better household-member selection UX
* Step 18 — Review artifact + payroll quality improvements
* Step 19 — Portfolio UI and richer household planning

## Important current truth

The biggest remaining functional product gap is still payroll approve/reject + canonical approval flow.

The UI foundation work is now complete enough that the next best move is to formalize payroll approval, rejection, canonicalization, and member ownership rules before building the dedicated Payroll page.