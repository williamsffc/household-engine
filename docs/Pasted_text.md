# Step 30 — Decision Metadata Summary Polish

Current active step.

## Context

Household Engine is complete through Step 29 and is now best described as:

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
* latest decision summary in review-oriented detail views

## Step 14A–29 status

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
* latest decision summary above the lifecycle list

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* history/decision surfacing should help users understand status quickly
* the UI should prefer compact, honest summaries over dense audit presentation

## Goal of Step 30

Add a small “decision metadata” summary block so the most important decision-specific details are visible immediately without requiring users to scan lifecycle details.

## Product intent

Right now the app shows:

* latest decision summary
* recent lifecycle list
* rejection reason in some places

This step should tighten that into a cleaner, more obvious summary of the current decision state, especially when:

* a paystub is currently rejected
* a paystub was recently reopened
* a useful reason exists

## Required outcome

Add compact decision metadata surfacing with focus on:

1. clear rejection reason display when currently rejected
2. clear reopen reason/context when recently reopened and available
3. calm, compact placement near latest decision summary
4. no regression to recent lifecycle list
5. no regression to workflow semantics
6. no regression to analytics semantics

## Scope guidance

This is a small trust/traceability polish step, not a new workflow system.

That means:

* use already-available decision/audit data where possible
* keep the UI compact
* avoid duplicate clutter
* keep the recent lifecycle list below for deeper detail
* do not redesign the pages
* do not build a full history viewer

## Suggested focus areas

### Current rejected state

If the paystub is currently rejected and a rejection reason exists, make it very visible.

### Recently reopened state

If the latest decision is reopen and an optional reason exists, surface it clearly.

### Placement

Best likely surfaces:

* Payroll detail
* Review Queue detail, where useful

Keep it near the latest decision summary.

## Files likely involved

Review first:

* `src/api/routes_review.py`
* `src/api/routes_payroll.py`
* `static/js/review_queue.js`
* `static/js/payroll.js`
* `static/css/app.css`

## Deliverables for this step

1. compact decision metadata summary
2. clearer visibility of rejection/reopen reasons where available
3. preserved latest-decision summary
4. preserved recent lifecycle list
5. no regression to workflow or analytics semantics

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no full timeline/versioning system
* no unrelated global redesign
* keep the system local-first and honest about history/state

## What comes next after Step 30

After Step 30, next work should likely be chosen from:

* additional extraction refinement
* command-center polish based on real usage
* further modest review-quality improvements