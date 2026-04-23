# Step 32 — Real-Usage Polish Pass

Current active step.

## Context

Household Engine is complete through Step 31 and is now best described as:

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

## Step 14A–31 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* the product should now be refined based on real usage, not abstract roadmap expansion
* polish should stay honest, modest, and high-value

## Goal of Step 32

Do a real-usage-driven polish pass across the current app, fixing the highest-value remaining rough edges without opening a new subsystem.

## Product intent

The major workflows now exist.

This step should focus on:

* small but recurring friction
* readability annoyances
* modest consistency gaps
* calm UX cleanup based on how the app actually feels in use

This is a stabilization step, not a feature expansion step.

## Required outcome

1. identify the highest-value small rough edges in the current app
2. fix a modest set of them cleanly
3. improve consistency/readability/usability across key pages
4. preserve current workflow semantics
5. preserve current analytics semantics
6. avoid introducing large new scope

## Scope guidance

This is a polish/stabilization step.

That means:

* fix a few concrete issues that noticeably improve everyday use
* prefer shared fixes over one-off hacks where possible
* keep changes incremental
* do not open a large new feature track
* do not redesign the app
* do not invent new scoring/analytics systems

## Suggested focus areas

Potential candidates:

* small Review Queue readability or aftermath-state polish
* small Payroll detail readability polish
* small Overview/Portfolio consistency cleanup
* spacing/stacking consistency
* wording clarity
* modest extraction warning presentation cleanup
* small cache-bust/static freshness cleanup where still needed

## Files likely involved

Review first based on the actual rough edges found, but likely:

* `static/css/app.css`
* `static/js/review_queue.js`
* `static/js/payroll.js`
* `static/js/overview.js`
* `static/js/portfolio.js`
* relevant templates:
  * `src/templates/review_queue.html`
  * `src/templates/payroll.html`
  * `src/templates/overview.html`
  * `src/templates/portfolio.html`

Potentially inspect:
* `src/api/routes_review.py`
* `src/api/routes_payroll.py`

## Deliverables for this step

1. a small set of real-usage-driven UX/readability fixes
2. better consistency across key pages where useful
3. no regression to workflow semantics
4. no regression to analytics semantics
5. no large new subsystem or redesign

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no full history/versioning system
* no fake confidence scoring
* no unrelated global redesign
* keep the system local-first and honest about data quality/state

## What comes next after Step 32

After Step 32, reassess based on actual use and remaining friction rather than committing to a large preset roadmap.