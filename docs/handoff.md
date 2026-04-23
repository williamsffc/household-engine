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
* Step 20
* Step 21
* Step 22
* Step 23
* Step 24
* Step 25
* Step 26
* Step 27
* Step 28
* Step 29
* Step 30
* Step 31
* Step 32
* Step 33

Current active step:

* Step 34 — Conflict-Aware UI Refresh for Review Actions

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
* plus Portfolio controls + recompute UX
* plus persistent shell scroll behavior
* plus Overview household readiness strip
* plus improved native-text payroll extraction quality
* plus scanned-PDF OCR fallback support
* plus controlled reopen / undo workflow for payroll decisions
* plus OCR / noisy-draft review hints
* plus richer review artifact / audit surfacing
* plus latest decision summary
* plus compact decision metadata summary
* plus review/traceability readability polish
* plus real-usage polish improvements
* plus backend workflow safety hardening

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
* reopen / undo workflow now exists
* persisted payroll review artifacts now exist
* persisted payroll decision metadata now exists
* native-text payroll extraction quality improved
* scanned-PDF OCR fallback exists with honest source signaling
* targeted extraction follow-ups exist
* review-side hints now exist:
  * OCR source hinting
  * sparse/noisy line-detail hinting
* recent lifecycle history now exists in Review Queue and Payroll detail
* review artifact metadata now surfaces in Review Queue detail
* latest decision summary now appears in Review Queue and Payroll detail
* compact decision metadata summary now appears in Review Queue and Payroll detail
* audit rows now use human-readable labels and cleaner summarized details
* decision metadata row now also shows decided_at / decision_actor when present
* backend approve/reject/reopen actions are now hardened:
  * conditional updates only
  * SQLite transaction protection
  * stale/no-op requests return 409 Conflict
  * duplicate/no-op audit writes are avoided

### Payroll page

* dedicated Payroll page exists
* Payroll route is wired into UI routing
* Payroll appears in shared navigation
* payroll list/detail browsing exists
* payroll payloads are enriched for UI
* household-vs-per-person payroll browsing exists
* payroll status presentation is clearer across approved / rejected / in_review
* Payroll detail shows rejection reason when present
* Payroll detail supports reopening approved/rejected payroll back into review
* Payroll detail shows recent lifecycle history, OCR/noisy-draft hints, latest decision summary, and decision metadata summary

### Portfolio / planning

* dedicated Portfolio page exists
* Portfolio route is wired into UI routing
* Portfolio appears in shared navigation
* Portfolio UI consumes the existing `/api/overview/portfolio` endpoint
* Portfolio shows deployable surplus / planning summary
* Portfolio shows supporting assumptions and recent cashflow context
* Portfolio shows honest limited/unavailable warning states when approved payroll is missing or insufficient
* Portfolio remains a modest, household-first planning surface
* Portfolio controls exist
* recompute/apply UX exists
* Reset to defaults exists
* current assumptions summary exists
* current control values are reflected in the URL query string
* UI-side duplicate-submit prevention exists for recompute/apply
* approved-only payroll semantics remain unchanged

### Shared analytics / overview

* cashflow analytics views
* overview dashboard UI
* trend / forecast endpoints
* portfolio / deployable-surplus endpoint
* overview readiness endpoint/strip exists
* readiness reflects approved payroll presence, expense-history coverage, in-review queue depth, and planning availability
* `/api/overview/summary` now returns truthful pending_reviews and payroll_ready
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
* responsive shared navigation already exists across large / medium / small layouts
* topbar/header is now persistent
* navigation is now persistent
* main content region is now the primary scrollable area
* mobile drawer behavior remains in place with main scroll locking while open
* shared spacing bugfix applied and cache-busted

### Shared upload interaction layer

* shared upload surface helper exists in shared JS
* upload surface is reusable across pages
* drag-and-drop + click-to-upload supported
* upload states include idle, drag-over, uploading, success, and error
* current upload integration uses existing `POST /api/documents/upload`

### Real-usage polish from Step 32

* Review Queue and Payroll rows are keyboard-activatable
* clearer hover/focus styling on clickable rows
* Review Queue no longer risks a null crash for `rq-detail-meta`
* Approve/Reject/Reopen/Apply buttons now disable and show working state during requests
* duplicate-submit prevention improved on the UI side

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
* `GET /api/overview/readiness`

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
* `POST /api/review-queue/{document_id}/reopen`

### Household API

* `GET /api/household/members`

## Product rule now locked in

The app is **household-first**, but every payroll record belongs to exactly **one household member**.

This means:

* payroll is tracked per member
* approved payroll analytics support both per-member views and household combined rollups
* household payroll totals are computed from approved per-member payroll
* household planning remains grounded in approved household cashflow

## What is not implemented yet

### Frontend conflict handling

* frontend does not yet gracefully interpret backend 409 Conflict responses for approve/reject/reopen
* stale/no-op action attempts could still surface as generic errors rather than calm refresh-to-truth behavior

### Deferred advanced items

* no visual PDF redaction
* no field-level extraction confidence
* no full auth / user-role system
* no broader advanced anomaly scoring yet
* no brokerage integrations

## Immediate recommended next work

Proceed with:

* Step 34 — Conflict-Aware UI Refresh for Review Actions

## Important current truth

The backend review actions are now safer.

The next best move is to make the frontend respond calmly to 409 conflict/no-op situations by refreshing toward backend truth instead of treating them like generic errors.