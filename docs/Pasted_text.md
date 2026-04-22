# Step 22 — Overview Household Readiness Strip

Current active step.

## Context

Household Engine is complete through Step 21 and is now best described as:

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

The app currently has:

* local-first FastAPI + SQLite Hub
* working Expenses ingest, analytics, and UI
* working Payroll draft ingest, payroll APIs, and review queue backend/UI
* shared cashflow analytics, trends, forecast, and portfolio summary endpoint
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
* Portfolio controls for trailing months / liquidity reserve months
* persistent topbar/nav with main-content scrolling

## Step 14A–21 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* the UI should stay honest about data readiness, incomplete inputs, and limited outputs
* the Overview page should increasingly behave like a true command center

## Goal of Step 22

Add a modest “household readiness” strip to the Overview page so the app surfaces the current state of household financial readiness in one place.

This should make it easier to answer questions like:

* do we have approved payroll yet?
* do we have enough expense history to trust recent summaries?
* are there still items waiting in review?
* is the household planning/portfolio layer operating on strong or limited inputs?

## Product intent

This step should improve clarity, not add complexity.

The readiness strip should:

* be quick to scan
* feel calm and honest
* summarize the current state of key data readiness signals
* reinforce the command-center nature of the Overview page

## Required outcome

Add an Overview readiness strip or equivalent top-level status area that communicates, in a modest way:

1. whether approved payroll is present
2. whether there is recent expense coverage / useful expense history
3. whether items are currently in review
4. whether planning/portfolio outputs are likely strong vs limited
5. clear, honest states rather than fake confidence

## Scope guidance

This is an Overview clarity step, not a new analytics engine.

That means:

* build a modest readiness/status surface
* reuse existing backend truth where possible
* keep the UI lightweight and readable
* do not invent fake scoring
* do not redesign the whole Overview page
* do not broaden into new portfolio logic
* do not start payroll extraction work yet

## Suggested focus areas

### Readiness signals

Potential readiness indicators include:

* Approved payroll present / missing
* Expense history coverage available / thin
* Pending review items count
* Planning input quality limited / usable

### Overview placement

The strip should likely live high on the Overview page so it becomes part of the user’s first scan of the app.

### Honesty

States should remain simple and truthful, for example:

* Ready
* Limited
* Missing
* Pending review

Avoid fake numeric confidence or anything that implies more certainty than the system really has.

## Files likely involved

Review first:

* `src/templates/overview.html`
* `static/js/overview.js`
* `static/css/app.css`
* `src/api/routes_overview.py`

Potentially inspect whether existing overview/portfolio/review summary data already provides enough signals before adding new endpoints.

## Deliverables for this step

1. Overview readiness strip or equivalent status area
2. honest household readiness signals
3. no regression to current Overview page usability
4. no regression to shell scroll behavior
5. no regression to payroll/portfolio semantics

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no fake scoring system
* no unrelated global redesign
* keep the system local-first and honest about readiness/limitations

## What comes next after Step 22

After Step 22, the next roadmap order becomes:

* Step 23 — Payroll extraction quality improvements
* Step 24 — Scanned-PDF OCR support
* Step 25 — Reopen / undo workflow for payroll decisions

Additional later work can still include richer review artifact expansion if it continues to look worthwhile.