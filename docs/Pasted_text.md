# Step 16 — Dedicated Payroll Page / Paystub Examination UI

Current active step.

## Context

Household Engine is complete through Step 15 and is now best described as:

* V1-complete
* plus selective V2-ready hardening
* plus post-roadmap UI foundation refresh
* plus canonical payroll approval workflow

The app currently has:

* local-first FastAPI + SQLite Hub
* working Expenses ingest, analytics, and UI
* working Payroll draft ingest, payroll APIs, and review queue backend/UI
* shared cashflow analytics, trends, forecast, and portfolio summary endpoints
* Overview, Expenses, and Review Queue UI pages
* shared shell/theme foundation
* responsive shared navigation
* shared in-app upload component
* Expenses UX refresh
* Review Queue UX refresh
* payroll approve/reject + canonical approval flow

## Step 14A–14E status

Completed enough.

Delivered:

* shared shell/theme foundation
* responsive navigation
* shared in-app upload surface
* Expenses UX refresh
* Review Queue UX refresh

## Step 15 status

Completed enough.

Delivered:

* approve/reject payroll review actions
* canonical payroll workflow
* coherent state transitions across:
  * `documents.status`
  * `payroll_paystubs.status`
* member ownership enforcement:
  * payroll record belongs to exactly one household member
* approved-only payroll analytics preserved
* rejected payroll excluded from analytics
* Review Queue UI actions for approve/reject

## Product rule now locked in

The app is **household-first**, but every payroll record belongs to exactly **one household member**.

That means:

* payroll documents/paystubs are tracked per person
* approved payroll analytics must work both:
  * per person
  * household combined
* household totals are the rollup of approved per-member payroll
* the UI should support later views such as:
  * Household
  * Person-M
  * Person-W

## Goal of Step 16

Build the dedicated Payroll page / paystub examination UI.

This page should become the main place for browsing payroll history and examining payroll records, while the Review Queue remains focused on draft/in_review review work.

## Product intent

The Payroll page should make it easy to understand:

* what payroll records exist
* which are approved vs draft vs rejected
* which household member a record belongs to
* how to view household-combined payroll vs per-person payroll
* how to inspect a specific paystub in a cleaner payroll-focused UI

This should feel like a first-class product page, not just an API dump.

## Required outcome

Build a dedicated Payroll page that supports:

1. a Payroll navigation entry/page
2. payroll list / browsing experience
3. clear member ownership display
4. status visibility:
   * approved
   * draft / in_review
   * rejected
5. a clean paystub examination/detail view
6. ability to think in both:
   * household-combined terms
   * per-person terms
7. better payroll-focused readability than the Review Queue page

## Scope guidance

This step should build the Payroll page, but should not turn into a broad redesign or advanced analytics project.

That means:

* add the dedicated Payroll page
* support browsing/examining payroll records
* support member-aware filtering or grouping if practical
* keep the implementation modest and aligned with the current codebase
* do not build advanced portfolio logic here
* do not broaden into major OCR/parser work
* do not add a reopen/undo workflow yet unless a very small improvement is needed

## Suggested focus areas

### Payroll page structure

The page should likely answer:

* what payroll records exist right now
* who they belong to
* what their status is
* what details matter most for examination

### Household vs person view

The page should start supporting the product model:

* household-first overall
* per-person payroll beneath that

This could be expressed through:
* filters
* segmented view
* grouped list
* tabs
* or another modest pattern that fits the current codebase

### Paystub detail / examination

The detail area should make it easy to inspect:

* pay date
* period
* gross pay
* net pay
* member
* status
* key payroll lines
* source/review linkage if useful

### Relationship to Review Queue

Review Queue should remain focused on draft review work.

The Payroll page should become the cleaner destination for payroll browsing and examination across statuses.

## Files likely involved

Review first:

* `src/templates/base.html`
* `src/templates/payroll.html` if already present or create it if needed
* `src/api/routes_ui.py`
* `src/api/routes_payroll.py`
* `static/js/payroll.js`
* `static/css/app.css`

Also inspect:

* current payroll list/detail endpoints
* any existing templates or placeholder payroll route/page wiring

## Deliverables for this step

1. dedicated Payroll page
2. payroll route added to shared navigation
3. payroll list/browse UI
4. payroll detail/examination UI
5. member ownership shown clearly
6. status shown clearly
7. modest household-vs-person support in the page model
8. no regression to existing shell/upload/Expenses/Review Queue foundations

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no unrelated global redesign
* no advanced payroll forecasting expansion here
* keep the system local-first and honest about status/state

## What comes next after Step 16

If Step 16 lands cleanly, the next roadmap order becomes:

* Step 17 — Better household-member selection UX
* Step 18 — Review artifact + payroll quality improvements
* Step 19 — Portfolio UI and richer household planning