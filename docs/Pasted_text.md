# Step 28 — Richer Review Artifact / Audit Surfacing

Current active step.

## Context

Household Engine is complete through Step 27 and is now best described as:

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
* review-side OCR / sparse-line hints

## Step 14A–27 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* review history should be more visible, but still honest and modest
* audit surfacing should not become a full versioning system

## Goal of Step 28

Make review artifacts and audit history easier to inspect in the UI so users can better understand what happened to a payroll item over time.

This should improve trust and traceability without creating a complex history product.

## Product intent

Right now important review/audit information exists, but much of it is still hidden in backend structures:

* approve/reject/reopen events live in audit log
* persisted review artifacts exist
* decision metadata exists
* review and payroll pages show some of this, but not enough of the timeline/context

This step should expose the most useful parts of that history in a calm, readable way.

## Required outcome

Improve review artifact / audit surfacing with focus on:

1. better visibility into review decisions and reopen events
2. better visibility into persisted review context where useful
3. clearer traceability in Review Queue and/or Payroll detail
4. no regression to workflow semantics
5. no regression to member-aware payroll model
6. no full version-history system

## Scope guidance

This is a modest history/traceability step, not a full audit product.

That means:

* surface useful audit details already available
* surface key review/decsion context in the UI
* keep the implementation lightweight
* do not build full diff/version history
* do not redesign the whole review workflow
* do not add fake timeline certainty where data is thin

## Suggested focus areas

### Audit visibility

Potentially surface recent lifecycle events such as:

* approved
* rejected
* reopened

with basic details like:

* when
* actor
* optional reason where available

### Review artifact visibility

Potentially surface useful persisted artifact facts such as:

* extraction source
* redaction counts
* when persisted/generated
* whether OCR was involved

### Placement

Most likely useful places:

* Review Queue detail
* Payroll detail

Keep the history modest and readable.

## Files likely involved

Review first:

* `src/services/review_queue.py`
* `src/api/routes_review.py`
* `src/api/routes_payroll.py`
* `static/js/review_queue.js`
* `static/js/payroll.js`
* `static/css/app.css`

Potentially inspect:

* audit log access patterns
* persisted review artifact storage
* current payloads returned for review/payroll detail

## Deliverables for this step

1. richer review artifact / audit surfacing
2. clearer visibility of approve/reject/reopen history where practical
3. clearer visibility of useful review artifact metadata where practical
4. no regression to workflow semantics
5. no regression to analytics semantics
6. no full version-history system

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no full timeline/versioning system
* no unrelated global redesign
* keep the system local-first and honest about history/state

## What comes next after Step 28

After Step 28, next work should likely be chosen from:

* additional payroll extraction refinement
* command-center polish based on real usage
* further review-quality improvements where they prove useful