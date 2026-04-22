# Step 20 — Portfolio Controls + Recompute UX

Current active step.

## Context

Household Engine is complete through Step 19 and is now best described as:

* V1-complete
* plus selective V2-ready hardening
* plus post-roadmap UI foundation refresh
* plus canonical payroll approval workflow
* plus dedicated Payroll page / paystub examination UI
* plus better household-member selection UX
* plus improved payroll review artifact durability and traceability
* plus Portfolio UI / modest household planning surface

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

## Step 14A–19 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household planning remains a combined household surface
* planning numbers must stay grounded in:
  * approved payroll
  * expenses / household cashflow
* the UI must remain honest when outputs are conservative, limited, or unavailable
* no speculative optimizer behavior should be introduced

## Goal of Step 20

Make the Portfolio page more interactive and practically useful by adding small, honest controls for recomputing the planning result.

This is a refinement step, not a new planning engine.

## Product intent

Right now the Portfolio page works, but it uses backend defaults only.

This step should let the household explore a small range of assumptions safely, such as:

* how many trailing months are used
* how much liquidity reserve to hold back

without changing the underlying conservative planning model.

## Required outcome

Add a modest recompute UX on the Portfolio page that supports:

1. adjusting `trailing_months`
2. adjusting `liquidity_reserve_months`
3. recomputing the planning result from the existing backend model
4. preserving honest limited/unavailable states
5. preserving approved-payroll-only semantics
6. staying household-first

## Scope guidance

This is a portfolio refinement step, not an optimization or integrations step.

That means:

* keep the existing backend planning model
* expose a small number of safe controls
* add a simple Apply / Recompute interaction if useful
* keep the UI calm, honest, and understandable
* do not add brokerage integrations
* do not add advanced optimization, target allocation engines, or speculative forecast tuning
* do not redesign the whole Portfolio page

## Suggested focus areas

### Portfolio controls

Add clear controls for:

* trailing months
* liquidity reserve months

Use safe bounds and defaults.

### Recompute/apply flow

The user should be able to:

* change a control
* recompute the result
* understand that the output is still only a modest planning estimate

### Explanation / honesty

Make it clear that:

* the result is based on approved payroll + expenses
* changing the controls changes the estimate inputs, not the underlying truth
* unavailable/limited states should remain explicit

### Household-first framing

Even with controls, the Portfolio page should stay a household planning page, not a personal investing tool.

## Files likely involved

Review first:

* `src/api/routes_overview.py`
* `src/services/portfolio.py`
* `src/templates/portfolio.html`
* `static/js/portfolio.js`
* `static/css/app.css`

## Deliverables for this step

1. Portfolio page controls for `trailing_months`
2. Portfolio page controls for `liquidity_reserve_months`
3. recompute/apply UX
4. preserved honest limited/unavailable states
5. no regression to approved-payroll-only semantics
6. no regression to current Portfolio page clarity

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no brokerage integrations
* no advanced optimizer behavior
* no unrelated global redesign
* keep the system local-first and honest about assumptions

## What comes next after Step 20

After Step 20, the next work should likely be chosen based on practical value, for example:

* stronger payroll extraction quality
* scanned-PDF OCR support
* richer portfolio/planning refinement
* additional review artifact improvements