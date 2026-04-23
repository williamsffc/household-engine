# Step 29 — Latest Decision Summary

Current active step.

## Context

Household Engine is complete through Step 28 and is now best described as:

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

## Step 14A–28 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* history surfacing should help users understand what happened quickly
* the UI should prefer concise, honest summaries over overly dense audit presentation

## Goal of Step 29

Add a small “Latest decision” summary line or block so users can immediately see the most important recent payroll decision without scanning the full lifecycle list.

## Product intent

Right now the app shows recent lifecycle history, which is useful, but users still have to scan it.

This step should answer, at a glance:

* what was the latest important decision?
* when did it happen?
* was it approved, rejected, or reopened?
* was there a reason, if available?

The goal is faster understanding, not a bigger audit console.

## Required outcome

Add a concise latest-decision summary with focus on:

1. latest approve/reject/reopen event
2. timestamp
3. optional reason when available
4. calm, readable placement in Review Queue and/or Payroll detail
5. no regression to current recent-lifecycle display
6. no regression to workflow semantics

## Scope guidance

This is a small traceability polish step, not a new history system.

That means:

* derive the latest decision summary from existing audit rows
* keep the UI compact
* keep the full recent-lifecycle list available below
* do not add a full timeline browser
* do not redesign the pages

## Suggested focus areas

### Latest decision summary

Potential content:

* Latest decision: Approved / Rejected / Reopened
* When: timestamp
* Why: optional reason if present

### Placement

Best likely surfaces:

* Review Queue detail
* Payroll detail

Keep it above the longer lifecycle list so users get the answer quickly.

### Modesty

Only summarize the latest meaningful lifecycle decision, not every event.

## Files likely involved

Review first:

* `src/api/routes_review.py`
* `src/api/routes_payroll.py`
* `static/js/review_queue.js`
* `static/js/payroll.js`
* `static/css/app.css`

## Deliverables for this step

1. latest decision summary in review-oriented detail views
2. preserved recent lifecycle list
3. no regression to audit/history surfacing
4. no regression to workflow semantics
5. no regression to analytics semantics

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no full timeline/versioning system
* no unrelated global redesign
* keep the system local-first and honest about history/state

## What comes next after Step 29

After Step 29, next work should likely be chosen from:

* additional payroll extraction refinement
* command-center polish based on real usage
* further modest review-quality improvements