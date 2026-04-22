# Step 23 — Payroll Extraction Quality Improvements

Current active step.

## Context

Household Engine is complete through Step 22 and is now best described as:

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

## Step 14A–22 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* extraction quality improvements must preserve ownership, review honesty, and approval semantics

## Goal of Step 23

Improve payroll extraction quality on the current native-text path so payroll details become more complete, more useful, and more trustworthy before adding scanned-PDF OCR support.

This step should make draft payroll outputs better without changing the honest review-driven workflow.

## Product intent

Right now payroll extraction works, but quality is still thin in practical ways:

* payroll lines are often sparse or empty
* some important fields may be missing even when text exists
* draft detail completeness varies too much
* the system is usable, but not yet as strong as it could be on native-text PDFs

This step should improve extraction quality where the existing path already has enough text to do better.

## Required outcome

Improve payroll extraction quality with focus on:

1. stronger field extraction where low-risk improvements are possible
2. better payroll line capture where practical
3. better normalization/cleanup of extracted payroll detail
4. clearer handling of partially inferred vs missing data
5. no regression to review queue honesty
6. no regression to member ownership or approval/canonical semantics

## Scope guidance

This is a quality-improvement step for the current extraction path, not an OCR step yet.

That means:

* improve extraction from native-text payroll documents
* improve parsed detail quality where current heuristics are thin
* improve line-item usefulness if practical
* keep the system review-driven and honest
* do not start scanned-PDF OCR support yet
* do not redesign the whole payroll workflow
* do not change approved-only analytics rules

## Suggested focus areas

### Field extraction quality

Look for high-value improvements to fields like:

* pay date
* period start/end
* gross pay
* net pay
* regular pay / earnings
* taxes / deductions
* YTD values where available

### Payroll lines

Improve usefulness of `payroll_lines` where the current output is often sparse.

This can include:

* better line detection
* better normalization of line labels
* better category assignment
* better filtering of junk/duplicate rows

### Draft honesty

The system should remain honest about what was confidently extracted vs still missing.

It is better to be modest and correct than broad and misleading.

## Files likely involved

Review first:

* `src/payroll/ingest.py`
* `src/payroll/extractor_pdf.py`
* `src/payroll/normalizer.py`
* `src/payroll/validator.py`
* `src/payroll/repository.py`

Potentially inspect:

* review payload composition
* current payroll detail rendering in:
  * `static/js/review_queue.js`
  * `static/js/payroll.js`

## Deliverables for this step

1. improved native-text payroll extraction quality
2. improved payroll line usefulness where practical
3. clearer/more complete draft payroll detail
4. no regression to approval/canonical workflow
5. no regression to review artifact persistence
6. no regression to member-aware payroll model

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no scanned-PDF OCR work yet
* no unrelated global redesign
* keep the system local-first and honest about data quality/state

## What comes next after Step 23

After Step 23, the next roadmap order becomes:

* Step 24 — Scanned-PDF OCR support
* Step 25 — Reopen / undo workflow for payroll decisions