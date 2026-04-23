# Step 27 — OCR / Noisy-Draft Review Hints

Current active step.

## Context

Household Engine is complete through Step 26 and is now best described as:

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
* plus targeted payroll extraction follow-ups

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

## Step 14A–26 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* review UI should stay honest about noisy or limited extraction
* hints should remain descriptive, not fake confidence scoring

## Goal of Step 27

Add small, honest review-side hints for OCR-backed or suspiciously sparse/noisy payroll drafts so users can calibrate trust during review.

This should improve review clarity without changing the review model or introducing scoring.

## Product intent

Now that the system supports:

* better native-text extraction
* OCR fallback
* reopen / re-review
* targeted extraction cleanup

the next practical improvement is to make noisy drafts easier to recognize at review time.

The goal is not to predict correctness.  
The goal is to say, in a simple and honest way:

* this draft used OCR
* this draft may be sparse/noisy
* verify totals/lines carefully

## Required outcome

Add modest review hints with focus on:

1. OCR-backed draft visibility
2. simple descriptive warnings when extracted line detail looks unusually sparse or noisy
3. no fake confidence scores
4. no regression to review honesty
5. no regression to approval/canonical workflow
6. no regression to member-aware payroll model

## Scope guidance

This is a review-surface hinting step, not a scoring system.

That means:

* use simple thresholds or descriptive signals
* keep the messaging narrow and honest
* surface the hint in Review Queue and/or Payroll detail if useful
* do not invent confidence percentages
* do not redesign the whole review UI
* do not change approval semantics
* do not change analytics rules

## Suggested focus areas

### OCR-backed hinting

If extraction_source indicates OCR, surface a clear note such as:

* OCR draft — verify fields carefully

### Sparse/noisy line hints

If the extracted line count is unusually low or otherwise suggests limited detail, surface a small note such as:

* line detail is limited
* totals may require closer review

### Placement

Best likely surfaces:

* Review Queue selected-item detail
* Payroll detail view, where useful

Keep the hints subtle but visible.

## Files likely involved

Review first:

* `src/api/routes_review.py`
* `src/api/routes_payroll.py`
* `static/js/review_queue.js`
* `static/js/payroll.js`
* `static/css/app.css`

Potentially inspect:

* current validation_summary / extraction_source usage
* current review payload structure
* current payroll detail payload structure

## Deliverables for this step

1. honest OCR/noisy-draft review hints
2. simple threshold-based sparse-detail hinting if practical
3. no fake scoring/confidence
4. no regression to review workflow
5. no regression to analytics semantics
6. no regression to current UI foundations

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no fake confidence scoring
* no unrelated global redesign
* keep the system local-first and honest about data quality/state

## What comes next after Step 27

After Step 27, next work should likely be chosen from:

* richer review artifact / audit surfacing
* additional payroll extraction refinement
* command-center polish based on real usage