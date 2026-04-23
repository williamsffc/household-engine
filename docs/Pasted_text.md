# Step 34 — Conflict-Aware UI Refresh for Review Actions

Current active step.

## Context

Household Engine is complete through Step 33 and is now best described as:

* V1-complete
* plus selective V2-ready hardening
* plus post-roadmap UI foundation refresh
* plus canonical payroll approval workflow
* plus dedicated Payroll page / paystub examination UI
* plus better household-member selection UX
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
* plus backend safety hardening for review actions

The app currently has:

* local-first FastAPI + SQLite Hub
* working Expenses ingest, analytics, and UI
* working Payroll draft ingest, payroll APIs, and review queue backend/UI
* shared cashflow analytics, trends, forecast, portfolio, and readiness signals
* Overview, Expenses, Review Queue, Payroll, and Portfolio UI pages
* shared shell/theme foundation
* responsive shared navigation
* shared in-app upload component
* payroll approval/canonical workflow
* dedicated Payroll page with household-vs-person browsing
* improved member picker UX for payroll upload
* persisted redacted payroll review artifacts
* persisted payroll decision metadata
* first-class Portfolio UI page
* persistent topbar/nav with main-content scrolling
* Overview readiness strip
* better native-text payroll field and line extraction
* OCR fallback for scanned/image-like paystubs
* reopen workflow for mistaken payroll decisions
* recent lifecycle history + artifact metadata in Review Queue and Payroll detail
* latest decision + decision metadata summaries
* cleaner human-readable audit rows
* keyboard accessibility and action-state polish
* backend-side protection against duplicate/stale approve/reject/reopen requests

## Step 14A–33 status

Completed enough.

Delivered:

* shell/theme/navigation/upload foundation
* Expenses UX refresh
* Review Queue UX refresh
* canonical payroll approval workflow
* dedicated Payroll page
* better household-member selection UX
* persisted payroll review artifacts + decision metadata
* Portfolio UI backed by approved-payroll-only planning logic
* Portfolio controls + recompute UX
* Reset to defaults + current assumptions summary
* persistent shell/topbar/nav with main content as the primary scroll region
* Overview readiness strip with honest household data-readiness signals
* improved native-text payroll extraction and payroll line usefulness
* scanned-PDF OCR fallback integrated into payroll ingest and review regeneration
* controlled reopen path for approved/rejected payroll items
* targeted OCR-friendly extraction cleanup and line classification improvements
* descriptive OCR/noisy-draft hints in Review Queue and Payroll detail
* recent lifecycle and review artifact metadata surfacing in Review Queue / Payroll detail
* latest decision summary and compact decision metadata
* human-readable audit rows and better traceability readability
* keyboard accessibility and UI-side duplicate-action prevention
* backend-side conditional-update hardening for approve/reject/reopen with 409 conflict responses on stale/no-op requests

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* UI should stay calm and truthful when backend state has already changed
* conflict handling should refresh toward backend truth, not guess

## Goal of Step 34

Make the Review Queue and Payroll UI handle backend `409 Conflict` responses gracefully for review actions.

## Product intent

Step 33 made the backend safer.  
This step should make the frontend feel safer too.

When users hit a stale or duplicate action case, the UI should:

* explain briefly what happened
* refresh the relevant list/detail state
* avoid leaving the user in a confusing or broken state

## Required outcome

1. handle 409 responses from approve/reject/reopen cleanly
2. show a calm, understandable message
3. refresh list/detail state to match backend truth
4. avoid duplicate/noisy error handling
5. preserve current workflow semantics
6. preserve current analytics semantics

## Scope guidance

This is a frontend conflict-handling step, not a workflow redesign.

That means:

* improve how the UI responds to stale/no-op action attempts
* keep the change small and explicit
* reuse existing banners/status areas
* do not redesign the pages
* do not change backend semantics again

## Suggested focus areas

### Review Queue actions

For approve/reject:
* detect 409
* show message like:
  * already decided
  * state changed
  * refreshing…
* refresh selected item / list state

### Payroll reopen action

For reopen:
* detect 409
* show message like:
  * already reopened or state changed
* refresh detail and/or navigate appropriately

### UX tone

Keep messages:
* brief
* calm
* truthful
* not alarming

## Files likely involved

Review first:

* `static/js/review_queue.js`
* `static/js/payroll.js`

Potentially inspect:
* current action fetch/error handling
* current banner/status rendering patterns
* endpoints in `src/api/routes_review.py` only to confirm 409 response shape if needed

## Deliverables for this step

1. conflict-aware UI handling for approve/reject/reopen
2. calm user-visible messaging
3. automatic refresh to backend truth where appropriate
4. no regression to workflow semantics
5. no regression to analytics semantics

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no workflow redesign
* no unrelated global redesign
* keep the system local-first and honest about workflow state

## What comes next after Step 34

After Step 34, reassess based on real usage again, likely choosing between:

* more command-center polish
* more extraction refinement
* small workflow readability improvements