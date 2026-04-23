# Step 31 — Review, Traceability, and Command-Center Polish

Current active step.

## Context

Household Engine is complete through Step 30 and is now best described as:

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
* compact latest-decision + decision-metadata summaries

## Step 14A–30 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* review surfaces should be trustworthy, readable, and modest
* polish work should improve clarity and trust without creating heavy new systems

## Goal of Step 31

Do one combined polish/stabilization pass across review UX, traceability, extraction rough edges, and command-center consistency.

This should tighten the app based on real usage without opening a large new subsystem.

## Product intent

This step combines several small-but-related improvements into one refinement pass:

1. review polish
2. traceability polish
3. extraction follow-up polish
4. command-center polish

The goal is to make the app feel more trustworthy, more readable, and more coherent in everyday use.

## Required outcome

### Review / traceability polish

1. improve decision/time/actor visibility where useful
2. improve reason visibility where useful
3. keep lifecycle/review context easy to scan
4. preserve modest scope and avoid full history/versioning UI

### Extraction follow-up polish

5. make a few targeted heuristic improvements based on real weak spots
6. improve OCR/native draft usefulness where low-risk
7. avoid broad parser rewrites or fake confidence scoring

### Review workflow polish

8. improve small empty states / aftermath states / guidance text where useful
9. make “why this needs review” and “what happened” slightly clearer

### Command-center polish

10. improve small cross-page consistency/readability/spacing where useful
11. keep the persistent shell stable and calm
12. avoid broad redesign

## Scope guidance

This is a combined refinement step, not a new platform phase.

That means:

* focus on small high-value improvements
* prioritize polish based on real friction
* reuse existing backend truth and UI patterns
* avoid major new features
* avoid subsystem sprawl

## Suggested focus areas

### Review / Payroll detail

* compact traceability improvements
* decision/timestamp/actor clarity
* reason visibility
* calmer review messaging

### Extraction follow-ups

* recurring OCR/native label cleanup
* recurring line classification edge cases
* a few targeted heuristics only

### Cross-page polish

* spacing consistency
* readability consistency
* minor hierarchy/wording cleanup
* stable shell behavior

## Files likely involved

Review first:

* `static/js/review_queue.js`
* `static/js/payroll.js`
* `static/js/overview.js`
* `static/css/app.css`

Potentially inspect:

* `src/api/routes_review.py`
* `src/api/routes_payroll.py`
* `src/payroll/ingest.py`
* `src/payroll/normalizer.py`
* `src/templates/review_queue.html`
* `src/templates/payroll.html`
* `src/templates/overview.html`
* `src/templates/portfolio.html`

## Deliverables for this step

1. a modest set of high-value review/traceability polish improvements
2. a modest set of high-value extraction follow-up improvements
3. a modest set of command-center/readability polish improvements
4. no regression to workflow semantics
5. no regression to analytics semantics
6. no regression to member-aware payroll model

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no full version-history system
* no fake confidence scoring
* no unrelated global redesign
* keep the system local-first and honest about data quality/state

## What comes next after Step 31

After Step 31, reassess based on real usage and actual friction rather than committing to a large preset roadmap.