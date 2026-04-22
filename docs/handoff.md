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
* Step 15
* Step 16
* Step 17
* Step 18
* Step 19

Current active step:

* Step 20 — Portfolio controls + recompute UX

## Current status

Household Engine is now:

* V1-complete
* plus selective V2-ready hardening
* plus UI foundation refresh completed enough to support next workflow work
* plus canonical payroll approval workflow
* plus dedicated Payroll page / paystub examination UI
* plus improved household-member selection UX
* plus improved payroll review artifact durability and traceability
* plus Portfolio UI / modest household planning surface

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
* household-member picker now exists for payroll upload
* last-used payroll upload member persists locally
* clearer ownership messaging during payroll upload
* clearer upload hierarchy and `in_review` explanation
* more scannable selected-item detail layout
* calmer loading states and partial-failure behavior
* approve/reject review actions now exist
* canonical payroll status transitions now exist
* ownership mismatch protection exists for review decisions
* approved payroll becomes analytics-eligible
* rejected payroll stays out of analytics
* persisted payroll review artifacts now exist
* persisted payroll decision metadata now exists:
  * decided_at
  * decision_actor
  * rejection_reason

### Payroll page

* dedicated Payroll page exists
* Payroll route is wired into UI routing
* Payroll appears in shared navigation
* payroll list/detail browsing exists
* payroll payloads are enriched for UI:
  * member display name / role
  * document status
  * original filename
  * uploaded timestamp
* household-vs-per-person payroll browsing exists
* payroll status presentation is clearer across approved / rejected / in_review
* Payroll detail shows rejection reason when present

### Portfolio / planning

* dedicated Portfolio page exists
* Portfolio route is wired into UI routing
* Portfolio appears in shared navigation
* Portfolio UI consumes the existing `/api/overview/portfolio` endpoint
* Portfolio shows deployable surplus / planning summary
* Portfolio shows supporting assumptions and recent cashflow context
* Portfolio shows honest limited/unavailable warning states when approved payroll is missing or insufficient
* Portfolio remains a modest, household-first planning surface
* approved-only payroll semantics remain unchanged

### Shared analytics / overview

* cashflow analytics views
* overview dashboard UI
* trend / forecast endpoints
* portfolio / deployable-surplus endpoint
* payroll analytics remain approved-only
* household totals remain the rollup of approved per-member payroll

### Shared shell / UI foundation

* shared base shell across current UI pages
* semantic theme token system in shared CSS
* light mode default
* dark mode support
* theme toggle in shared shell
* theme preference persisted locally
* early theme initialization to reduce flash on load
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

## Current implemented routes

### UI

* `GET /`
* `GET /expenses`
* `GET /review-queue`
* `GET /payroll`
* `GET /portfolio`

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
* `POST /api/review-queue/{document_id}/approve`
* `POST /api/review-queue/{document_id}/reject`

### Household API

* `GET /api/household/members`

## Product rule now locked in

The app is **household-first**, but every payroll record belongs to exactly **one household member**.

This means:

* payroll is tracked per member
* approved payroll analytics support both:
  * per-member views
  * household combined rollups
* household payroll totals are computed from approved per-member payroll
* household planning remains grounded in approved household cashflow

This is the intended model for Person-M and Person-W going forward.

## What is not implemented yet

### Portfolio / planning refinement

* Portfolio page still uses backend defaults only
* no UI controls yet for `trailing_months`
* no UI controls yet for `liquidity_reserve_months`
* no recompute/apply UX yet for planning assumptions

### Payroll quality / later enhancements

* scanned-PDF/OCR robustness still needs improvement
* payroll line detail can still be sparse

### Review queue / lifecycle refinements

* no reopen/undo workflow yet for approve/reject

### Deferred advanced items

* no visual PDF redaction
* no field-level extraction confidence
* no full auth / user-role system
* no broader advanced anomaly scoring yet
* no brokerage integrations yet

## Immediate recommended next work

Proceed with:

* Step 20 — Portfolio controls + recompute UX

## Important current truth

The Portfolio page now exists and is honest/useful, but it still uses fixed backend defaults.

The next best move is to add small, safe controls for planning assumptions so the household can recompute the estimate without changing the underlying modest planning model.