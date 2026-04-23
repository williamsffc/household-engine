# Step 25 — Reopen / Undo Workflow for Payroll Decisions

Current active step.

## Context

Household Engine is complete through Step 24 and is now best described as:

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

## Step 14A–24 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* review decisions should remain auditable and reversible in a controlled way
* reopening a decision must preserve honesty about workflow state

## Goal of Step 25

Add a controlled reopen / undo workflow for payroll decisions so previously approved or rejected payroll items can be returned to review when needed.

This should be a modest lifecycle refinement, not a broad workflow rewrite.

## Product intent

Right now approve/reject is terminal.

That is workable, but less forgiving when:

* OCR fallback produces noisy drafts
* extraction quality improves after a re-ingest
* a user approves/rejects too quickly
* a mistake is noticed later

This step should add a controlled way to move a payroll item back into review without weakening the overall review-driven model.

## Required outcome

Add reopen / undo support with focus on:

1. reopening previously approved payroll back to review
2. reopening previously rejected payroll back to review
3. preserving member ownership truth
4. preserving auditability of decisions
5. handling analytics consequences honestly when approved payroll is reopened
6. keeping the Review Queue / Payroll page semantics understandable

## Scope guidance

This is a lifecycle refinement step, not a redesign of the payroll system.

That means:

* add a modest reopen path
* update statuses coherently
* preserve approval/canonical semantics
* preserve audit trail
* keep UI additions narrow and clear
* do not add a full version-history system
* do not redesign the whole review workflow

## Suggested focus areas

### Reopen semantics

Define the intended status transition clearly, for example:

* approved -> in_review / draft
* rejected -> in_review / draft

The reopened item should become reviewable again.

### Analytics correctness

If an approved payroll item is reopened:

* it should stop counting toward approved-only analytics
* household/per-member totals should stay truthful

### Auditability

Reopen events should be clearly recorded.

If practical, capture a simple reopen reason.

### UI placement

The most likely places for reopen controls are:

* Payroll page detail
* Review Queue detail for eligible items if appropriate

Keep the UI modest and honest.

## Files likely involved

Review first:

* `src/services/review_queue.py`
* `src/api/routes_review.py`
* `src/api/routes_payroll.py`
* `src/payroll/repository.py`
* `src/templates/review_queue.html`
* `src/templates/payroll.html`
* `static/js/review_queue.js`
* `static/js/payroll.js`

Potentially inspect:

* audit log writing
* review payload composition
* any queries that assume approved/rejected are terminal forever

## Deliverables for this step

1. reopen / undo workflow for approved/rejected payroll decisions
2. coherent status transitions back into review
3. preserved audit trail
4. truthful analytics behavior when reopened items leave approved status
5. modest UI support where appropriate
6. no regression to member-aware payroll model

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no unrelated global redesign
* no full history/versioning system
* keep the system local-first and honest about workflow state

## What comes next after Step 25

After Step 25, next work should be chosen based on the highest practical value, likely from:

* additional payroll extraction quality improvements
* richer review artifact expansion
* broader document-quality refinements