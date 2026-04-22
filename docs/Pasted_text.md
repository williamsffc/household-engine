# Step 21 — Portfolio Polish + Persistent Shell Scroll Behavior

Current active step.

## Context

Household Engine is complete through Step 20 and is now best described as:

* V1-complete
* plus selective V2-ready hardening
* plus post-roadmap UI foundation refresh
* plus canonical payroll approval workflow
* plus dedicated Payroll page / paystub examination UI
* plus better household-member selection UX
* plus improved payroll review artifact durability and traceability
* plus Portfolio UI / modest household planning surface
* plus Portfolio controls + recompute UX

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

## Step 14A–20 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household planning remains a combined household surface
* planning numbers must stay grounded in:
  * approved payroll
  * expenses / household cashflow
* the UI must remain honest when outputs are conservative, limited, or unavailable
* the shell should now feel more like a stable command-center frame

## Goal of Step 21

Polish the Portfolio page and improve the app shell so the header/navigation remain persistent while the inner page content scrolls.

This should make the app feel more stable and dashboard-like, especially on desktop, without overcomplicating mobile behavior.

## Product intent

This step has two tightly related goals:

### 1. Portfolio polish

Add small usability improvements such as:

* Reset to defaults
* clearer current assumptions summary
* cleaner small UX touches around recompute behavior

### 2. Persistent shell behavior

Refine the shared shell so that:

* topbar/header remains persistent
* navigation remains persistent
* the main page content becomes the primary scrollable region

This should improve orientation and usability across Overview, Expenses, Review Queue, Payroll, and Portfolio.

## Required outcome

### Portfolio polish

1. add Reset to defaults control
2. add a small “Current assumptions” summary
3. preserve existing recompute behavior
4. preserve honest limited/unavailable states
5. preserve approved-payroll-only semantics

### Shared shell refinement

6. make header/topbar persistent
7. keep navigation persistent
8. make the inner main content area the primary scrollable region
9. keep the experience clean on desktop
10. avoid awkward nested-scroll behavior on smaller screens

## Scope guidance

This is a modest polish/refinement step, not a full shell rewrite.

That means:

* improve the Portfolio page a little
* improve the shared shell scrolling behavior
* keep the implementation incremental
* do not redesign every page
* do not create many competing scroll regions
* do not start payroll extraction work yet

## Suggested focus areas

### Portfolio page

Add:
* Reset to defaults
* assumptions summary near the cards
* small UX polish around control values and apply/recompute flow

### Shell layout

Prefer:
* persistent topbar
* persistent sidebar/nav on desktop
* main content region scrolls
* careful behavior on medium/small screens so the app does not feel cramped

### Responsiveness

Be careful not to make mobile/tablet behavior worse.

A good result is:
* desktop: stable shell, scrollable content region
* small screens: still usable, not trapped in awkward nested scroll

## Files likely involved

Review first:

* `src/templates/base.html`
* `src/templates/portfolio.html`
* `static/js/portfolio.js`
* `static/css/app.css`

Potentially inspect page wrappers/layout structure across:
* Overview
* Expenses
* Review Queue
* Payroll
* Portfolio

## Deliverables for this step

1. Reset to defaults control on Portfolio page
2. current assumptions summary on Portfolio page
3. persistent shell/topbar/nav behavior
4. main content area as primary scroll region
5. no regression to responsive shell behavior
6. no regression to Portfolio planning semantics
7. no regression to other current pages

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no brokerage integrations
* no advanced optimizer behavior
* no unrelated global redesign
* keep the system local-first and honest about assumptions/state

## What comes next after Step 21

After Step 21, the next roadmap order becomes:

* Step 22 — Payroll extraction quality improvements
* Step 23 — Scanned-PDF OCR support
* Step 24 — Reopen / undo workflow for payroll decisions
* Step 25 — Richer review artifact expansion