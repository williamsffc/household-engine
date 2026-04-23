# Step 35 — Review Workflow and Reliability Polish

Current active step.

## Context

Household Engine is complete through Step 34 and is now best described as:

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
* plus real-usage polish improvements
* plus backend workflow safety hardening
* plus conflict-aware UI refresh for review actions

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
* keyboard accessibility and action-state polish
* backend-side protection against duplicate/stale review actions
* frontend-side calm handling for backend conflict responses

## Step 14A–34 status

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
* keyboard accessibility and UI-side duplicate-action prevention
* backend-side conditional-update hardening for approve/reject/reopen
* conflict-aware UI refresh behavior for stale/no-op review actions

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* review workflows should feel calm, safe, and trustworthy
* polish work should reduce friction without opening large new systems

## Goal of Step 35

Do one combined polish/hardening pass across review workflow behavior, reliability, traceability readability, artifact freshness edge cases, and consistency of empty/partial-failure states.

## Product intent

This step combines a set of closely related improvements into one stabilization pass:

1. review action UX tightening
2. small backend/workflow reliability refinement
3. audit/traceability readability cleanup
4. review artifact robustness/freshness edge-case handling
5. consistency polish for empty and partial-failure states

The goal is to make the current app feel more trustworthy, less surprising, and more coherent in real use.

## Required outcome

### Review action UX tightening

1. improve approve/reject/reopen aftermath behavior
2. make selection/refresh behavior feel intentional
3. reduce “where did it go?” confusion after actions

### Reliability refinement

4. improve handling of duplicate/stale/no-op requests where practical
5. keep backend truth primary
6. avoid noisy audit writes or misleading state transitions

### Audit / traceability readability

7. improve readability of surfaced audit/history details
8. improve reason formatting where useful
9. keep traceability modest, not overwhelming

### Review artifact robustness

10. handle stale/missing/empty artifact situations more clearly
11. make regeneration/fallback behavior more understandable
12. avoid confusing blank or ambiguous artifact states

### Consistency polish

13. align empty-state and partial-failure patterns across key pages
14. improve small wording/readability consistency where useful
15. preserve the calm command-center feel

## Scope guidance

This is a combined refinement step, not a new feature track.

That means:

* fix a modest set of high-value friction points
* prefer shared fixes over scattered hacks
* keep the scope practical
* do not build a full versioning/audit console
* do not redesign the app
* do not open unrelated systems

## Suggested focus areas

### Review Queue / Payroll detail

* post-action refresh behavior
* selection stability
* calm stale/conflict messaging
* reason/history readability

### Review artifacts

* clearer handling when artifact metadata exists but content is limited
* clearer handling when regeneration is needed or content is unavailable
* modest truthfulness improvements, not a full artifact browser

### Empty / partial-failure consistency

Across:
* Review Queue
* Payroll
* Overview
* Portfolio

Aim for:
* clearer empty states
* more aligned “limited / unavailable / failed” wording
* consistent user expectations

## Files likely involved

Review first:

* `static/js/review_queue.js`
* `static/js/payroll.js`
* `static/js/overview.js`
* `static/js/portfolio.js`
* `static/css/app.css`

Potentially inspect:
* `src/api/routes_review.py`
* `src/api/routes_payroll.py`
* `src/services/review_queue.py`
* `src/payroll/review_artifacts.py`
* relevant templates:
  * `src/templates/review_queue.html`
  * `src/templates/payroll.html`
  * `src/templates/overview.html`
  * `src/templates/portfolio.html`

## Deliverables for this step

1. a modest set of high-value review workflow polish improvements
2. a modest set of reliability/state-handling improvements
3. a modest set of traceability readability improvements
4. a modest set of artifact robustness/empty-state improvements
5. better consistency across current pages
6. no regression to workflow semantics
7. no regression to analytics semantics
8. no regression to member-aware payroll model

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no full version-history system
* no fake confidence scoring
* no unrelated global redesign
* keep the system local-first and honest about state and data quality

## What comes next after Step 35

After Step 35, reassess based on actual use and remaining friction rather than committing to another large preset roadmap.