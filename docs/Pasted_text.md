# Step 36 — Cross-Page Empty/Partial-Failure Consistency Pass

Current active step.

## Context

Household Engine is complete through Step 35 and is now best described as:

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
* plus review workflow and reliability polish

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
* review action flash messaging and artifact freshness protection

## Step 14A–35 status

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
* post-action flash success/warning messaging and review artifact freshness/read-time regeneration safeguards

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* empty, limited, and failed states should feel calm and consistent across the app
* polish should keep improving coherence rather than adding new heavy systems

## Goal of Step 36

Do a focused consistency pass on empty states, partial-failure states, and limited-data messaging across the key pages so the app feels more coherent and less surprising.

## Product intent

The major workflows now exist and are fairly robust.

The next polish opportunity is consistency:
* similar situations should look and feel similar
* “empty,” “limited,” “unavailable,” and “failed” should use clearer, more aligned language
* banners and empty-state panels should feel like part of one system

## Required outcome

1. review current empty/partial-failure/limited states across key pages
2. align wording and presentation where practical
3. improve consistency without redesigning the pages
4. preserve current workflow semantics
5. preserve current analytics semantics
6. keep changes modest and low-risk

## Scope guidance

This is a cross-page polish step, not a new feature track.

That means:

* tighten wording and state presentation
* reuse existing banner/callout/empty-state patterns
* prefer shared fixes over page-specific hacks
* do not redesign layouts
* do not add major new backend work

## Suggested focus areas

### Review Queue / Payroll

* empty list states
* no-selection states
* artifact-limited or regeneration-warning states
* stale/conflict aftermath wording

### Overview / Portfolio

* limited-data wording
* unavailable/empty wording
* warning banner tone consistency

### Expenses

* empty activity/table states
* partial-failure banner consistency

## Files likely involved

Review first:

* `static/js/review_queue.js`
* `static/js/payroll.js`
* `static/js/overview.js`
* `static/js/portfolio.js`
* `static/js/expenses.js`
* `static/css/app.css`

Potentially inspect:
* relevant templates for page-specific empty-state markup

## Deliverables for this step

1. more consistent empty-state wording/presentation across key pages
2. more consistent partial-failure and limited-state wording/presentation
3. no regression to workflow semantics
4. no regression to analytics semantics
5. no broad redesign

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no unrelated global redesign
* keep the system local-first and honest about state and data quality

## What comes next after Step 36

After Step 36, reassess based on actual use again, likely choosing between:

* more extraction refinement
* more command-center polish
* small workflow readability improvements