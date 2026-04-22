# Step 19 — Portfolio UI and Richer Household Planning

Current active step.

## Context

Household Engine is complete through Step 18 and is now best described as:

* V1-complete
* plus selective V2-ready hardening
* plus post-roadmap UI foundation refresh
* plus canonical payroll approval workflow
* plus dedicated Payroll page / paystub examination UI
* plus better household-member selection UX
* plus improved payroll review artifact durability and traceability

The app currently has:

* local-first FastAPI + SQLite Hub
* working Expenses ingest, analytics, and UI
* working Payroll draft ingest, payroll APIs, and review queue backend/UI
* shared cashflow analytics, trends, forecast, and portfolio summary endpoint
* Overview, Expenses, Review Queue, and Payroll UI pages
* shared shell/theme foundation
* responsive shared navigation
* shared in-app upload component
* payroll approval/canonical workflow
* dedicated Payroll page with household-vs-person browsing
* improved member picker UX for payroll upload
* persisted redacted payroll review artifacts
* persisted payroll decision metadata

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
* coherent payroll/document status transitions
* member ownership enforcement
* approved-only payroll analytics preserved
* rejected payroll excluded from analytics

## Step 16 status

Completed enough.

Delivered:

* dedicated Payroll page
* Payroll nav entry + UI route
* payroll list/detail browse UI
* enriched payroll list/detail payloads for UI
* status clarity across approved / rejected / in_review
* household-vs-per-person payroll browsing
* clearer member ownership display

## Step 17 status

Completed enough.

Delivered:

* household-member picker for payroll upload in Review Queue
* active members loaded from household API
* last-used member selection persisted locally
* single-member auto-select behavior
* clearer upload ownership messaging
* reduced risk from raw/manual member_id entry

## Step 18 status

Completed enough.

Delivered:

* persisted payroll review artifacts in SQLite
* persisted redacted text + redaction counts metadata
* persisted payroll decision metadata:
  * decided_at
  * decision_actor
  * rejection_reason
* Payroll detail now shows rejection reason when present
* no regression to approval/canonical semantics or approved-only analytics

## Product rule now locked in

The app is **household-first**, but every payroll record belongs to exactly **one household member**.

That means:

* payroll documents/paystubs are tracked per person
* approved payroll analytics must work both:
  * per person
  * household combined
* household totals are the rollup of approved per-member payroll
* planning/portfolio views should remain household-first while respecting the underlying approved household cashflow model

## Goal of Step 19

Build a Portfolio UI and modest richer household planning layer on top of the existing approved-payroll + expenses + overview portfolio endpoint.

This should turn the current portfolio/deployable-surplus backend into a real user-facing page or section that helps answer:

* how much deployable surplus exists
* what the household can realistically set aside
* how current household cashflow supports basic planning decisions

## Product intent

This step should create a practical, honest planning experience — not an overpromising optimization engine.

The Portfolio UI should feel like:

* a modest household planning surface
* grounded in actual approved payroll + expense data
* clear about what is estimated vs known
* useful for routine household decision-making

## Required outcome

Build a Portfolio UI / planning experience that supports:

1. a Portfolio page or equivalent first-class UI surface
2. clear display of current deployable surplus / planning summary
3. connection to current approved-payroll-driven cashflow model
4. honest explanation of what the portfolio/planning number means
5. modest richer planning presentation beyond a raw endpoint response
6. no regression to household-first combined analytics model

## Scope guidance

This is a portfolio/planning UI step, not a full wealth platform.

That means:

* expose existing portfolio/deployable-surplus logic in the UI
* improve readability and usefulness of planning outputs
* add modest planning-oriented framing if practical
* keep assumptions conservative and honest
* do not broaden into brokerage integrations
* do not build advanced optimization or forecasting systems here
* do not redesign the whole application

## Suggested focus areas

### Portfolio page / route

Create a dedicated place to view planning/portfolio information.

This may be:

* a dedicated `/portfolio` page
* or another equally first-class UI surface if it fits the current structure better

### Planning summary

Help the user understand:

* what the current deployable surplus number means
* what inputs it depends on
* what approved payroll / expenses are contributing
* when the result is unavailable or conservative because data is incomplete

### Household-first presentation

This should remain a household-level planning page.

It can acknowledge underlying per-member payroll, but the planning result should remain household combined unless there is a very small, useful drill-down.

### Honesty and guardrails

The UI should make it clear when:

* payroll is incomplete
* there is not enough approved data
* the output is conservative / unavailable / zero for honest reasons

## Files likely involved

Review first:

* `src/api/routes_overview.py`
* `src/services/portfolio.py`
* `src/api/routes_ui.py`
* `src/templates/base.html`
* `src/templates/portfolio.html` if needed
* `static/js/portfolio.js` if needed
* `static/css/app.css`

## Deliverables for this step

1. Portfolio UI surface
2. route/navigation support if needed
3. display of deployable surplus / planning summary
4. honest explanation of inputs and limitations
5. no regression to existing overview/expenses/payroll/review queue pages
6. no regression to approved-only payroll semantics

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no brokerage integrations yet
* no advanced optimization engine
* no unrelated global redesign
* keep the system local-first and honest about data quality/assumptions

## What comes next after Step 19

After Step 19, the next work should likely be chosen based on product value and real usage, for example:

* stronger payroll extraction quality
* scanned-PDF OCR support
* richer portfolio/planning refinements
* persisted review artifact expansion