# Step 15 — Payroll Approval / Canonical Workflow

Current active step.

## Context

Household Engine is complete through Step 13 and is now best described as:

* V1-complete
* plus selective V2-ready hardening
* plus post-roadmap UI foundation refresh

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

The biggest remaining functional gap is still payroll approve/reject + canonical approval flow.

## Step 14A–14E status

Completed enough.

### Step 14A delivered

* semantic theme tokens
* light mode default
* dark mode support
* theme toggle
* theme persistence
* early theme init to reduce flash
* shell/chart color cleanup

### Step 14B delivered

* responsive shared navigation across large / medium / small widths
* large-screen full sidebar
* medium-screen collapsed icon rail
* small-screen topbar + menu button + off-canvas drawer + backdrop
* navigation no longer disappears on smaller widths
* cache-busted shared shell assets so current CSS/JS reliably load in-browser

### Step 14C delivered

* shared reusable in-app upload surface
* drag-and-drop + click-to-upload behavior
* upload states:
  * idle
  * drag-over
  * uploading
  * success
  * error
* Expenses upload placement
* Review Queue upload placement
* integration with existing document upload flow

### Step 14D delivered

* clearer Expenses page hierarchy
* labeled Upload panel at the top of Expenses
* calmer loading states
* partial-failure handling with inline banner instead of full-page failure
* safer chart re-render behavior
* better phone-width summary-card layout

### Step 14E delivered

* clearer Review Queue hierarchy
* labeled payroll upload panel
* explicit explanation of `in_review` meaning
* calmer loading states and partial-failure handling
* more scannable selected-item detail layout
* improved warning and redacted-text presentation
* better small-screen readability

## New product rule to lock in

The app is **household-first**, but every payroll record belongs to exactly **one household member**.

That means:

* payroll documents/paystubs are tracked per person
* approved payroll analytics must work both:
  * per person
  * household combined
* household totals are the rollup of approved per-member payroll
* the UI should later be able to support:
  * Household view
  * Person-M view
  * Person-W view

## Goal of Step 15

Implement the payroll approval / canonical workflow.

This is not just about adding buttons.

This step should formalize how payroll moves from:

* uploaded
* processing
* in_review
* approved or rejected

and how approved payroll becomes the canonical source for downstream analytics.

## Required outcome

Implement a clean payroll approval flow that:

1. allows a draft payroll review item to be approved
2. allows a draft payroll review item to be rejected
3. preserves which household member the payroll belongs to
4. ensures only approved payroll affects analytics
5. makes household totals the rollup of approved per-member payroll
6. keeps rejected items out of analytics
7. stays honest about draft vs approved vs rejected state

## Product/data rule for this step

Lock in this canonical rule:

* every payroll document/paystub must belong to exactly one household member
* approved payroll remains tied to that specific member
* household payroll analytics are the sum of approved paystubs across members

This step should support the real use case:

* uploading paystubs for Person-M
* uploading paystubs for Person-W
* tracking each person individually
* still using one shared household finance command center

## Scope guidance

This step should focus on canonical payroll workflow, not the dedicated Payroll page yet.

That means:

* build the approval/rejection flow
* wire it into review queue behavior and payroll status handling
* confirm analytics use only approved payroll
* keep the UI additions modest and truthful
* do not start the dedicated Payroll page yet
* do not turn this into a large redesign

## Suggested focus areas

### Approval / rejection actions

Support workflow for review items:

* approve current draft
* reject current draft
* optionally capture a simple rejection reason if practical

### Canonical state transitions

Ensure state transitions are coherent across:

* `documents.status`
* `payroll_paystubs.status`
* review queue visibility
* downstream analytics eligibility

### Member ownership

Make sure approval preserves ownership by member.

The system should remain capable of later supporting:

* combined household payroll analytics
* Person-M payroll history
* Person-W payroll history

### Analytics correctness

Reconfirm or adjust payroll analytics so that:

* only approved payroll counts
* per-member monthly payroll works correctly
* household combined payroll is a rollup of approved member payroll

### Review Queue support

The Review Queue should remain the place where payroll draft review occurs.

If small UI additions are needed to support approval/rejection, keep them narrow and aligned with the existing page.

## Files likely involved

Review first:

* `src/api/routes_review.py`
* `src/api/routes_payroll.py`
* `src/services/review_queue.py`
* `src/payroll/repository.py`
* `src/payroll/views.py`
* migrations / SQL views if needed
* `src/templates/review_queue.html`
* `static/js/review_queue.js`

Also inspect any member-related model/schema/table usage already present.

## Deliverables for this step

1. approve/reject workflow for payroll review items
2. canonical status transitions
3. approved payroll included in analytics correctly
4. rejected payroll excluded correctly
5. member ownership preserved through approval flow
6. household-combined + per-member analytics model supported at the data level
7. modest UI support in Review Queue if needed
8. no regression to existing shell/upload/Expenses/Review Queue UX foundation

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no dedicated Payroll page yet
* no unrelated global redesign
* keep the system local-first and honest about workflow state

## What comes next after Step 15

If Step 15 lands cleanly, the next roadmap order becomes:

* Step 16 — Dedicated Payroll page / paystub examination UI
* Step 17 — Better household-member selection UX
* Step 18 — Review artifact + payroll quality improvements
* Step 19 — Portfolio UI and richer household planning