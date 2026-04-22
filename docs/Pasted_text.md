# Household Engine — Current Step Plan

## Role of this document

This file is the **current step plan only**.

It should be:
- short
- actionable
- sequential
- updated whenever the active roadmap changes

It should not try to restate the entire architecture or full repo history.
For target design, use `architecture.md`.
For actual implemented state, use `handoff.md`.

---

## Current state before this plan

Completed:
- Step 1
- Step 2
- Step 2.5
- Step 3
- Step 3.5
- Step 4A
- Step 4B
- Step 5A
- Step 5B
- Step 5C
- Step 6
- Step 7
- Step 8
- Step 9
- Step 10
- Step 11
- Step 12
- Step 13

Project status now:
- V1-complete
- plus selective V2-ready hardening

---

## Why the roadmap is changing now

Before building the dedicated Payroll page, the app needs a stronger shared UI foundation.

The most important current UX issues are:
- upload still feels too tied to file/folder handling instead of the app UI
- navigation disappears on smaller browser widths
- the current visual treatment is too dark
- the app should support both light mode and dark mode

Because of that, the next slice should focus on the shared shell first, then payroll approval, then the Payroll page.

---

## Step 14A — Theme system + shell foundation

Goal:
Create a reusable UI foundation instead of applying one-off styling fixes.

Build:
- introduce semantic theme tokens / variables
- support light mode and dark mode
- make light mode the default starting direction unless existing implementation constraints strongly favor preserving current mode first
- add a theme toggle in the app shell/header
- persist theme preference locally
- normalize shared surfaces:
  - app background
  - card / panel background
  - borders
  - primary / secondary / muted text
  - status colors
- normalize shared spacing, radii, shadows, and page header styling

Done when:
- the app can switch between light and dark mode
- the shell looks coherent in both modes
- pages no longer depend on one-off hardcoded dark styling assumptions

---

## Step 14B — Responsive navigation overhaul

Goal:
Make navigation adapt across browser sizes instead of disappearing.

Build:
- large screens: full sidebar with labels
- medium screens: collapsed icon rail / compact sidebar
- small screens: compact menu or drawer pattern
- strong active-page state
- ensure theme toggle remains reachable in responsive layouts

Done when:
- navigation remains usable at smaller widths
- users can still move between Overview, Expenses, and Review Queue without losing orientation

---

## Step 14C — Shared in-app upload interaction layer

Goal:
Move the primary file interaction into the product UI.

Build:
- reusable drag-and-drop upload component
- click-to-upload fallback
- accepted file type guidance
- drag / uploading / success / failure states
- hook into existing upload/document-registry behavior
- keep the component generic enough to reuse on future Payroll page

Done when:
- the app has a shared upload surface pattern usable by multiple pages
- upload interactions feel app-driven rather than folder-driven

---

## Step 14D — Expenses UX refresh

Goal:
Make Expenses feel like a complete in-app workflow.

Build:
- add upload surface directly on `/expenses`
- show clearer document / ingest feedback
- align cards, charts, and tables with the new theme system
- improve responsive behavior and smaller-width readability
- tighten loading / empty / error states

Done when:
- users can upload expense documents directly from the Expenses page
- the page remains usable across smaller browser sizes
- the page visually fits the new shell direction

---

## Step 14E — Review Queue UX refresh

Goal:
Make Review Queue more useful and better aligned with the future payroll flow.

Build:
- add payroll upload surface directly on `/review-queue`
- improve pending-item list hierarchy
- improve detail-panel readability
- present validation warnings more clearly
- clearly message that in-review payroll is draft-only and does not affect analytics until approval

Done when:
- users can start payroll review from inside the Review Queue page
- the page clearly communicates review state and next-step meaning

---

## Step 15 — Payroll approval / canonical workflow

Goal:
Close the biggest remaining functional gap in the product.

Build:
- approve payroll action
- reject payroll action
- route and service support for approval decisions
- canonical payroll state transitions
- analytics inclusion only after approval
- audit logging for approval / rejection decisions
- review queue updates that reflect the new decision states

Done when:
- a payroll draft can move from in-review to approved or rejected
- approved payroll contributes to analytics
- rejected payroll does not
- the workflow is explicit and review-driven

---

## Step 16 — Dedicated Payroll page / paystub examination UI

Goal:
Add a payroll-focused page once the shell and approval model are ready.

Build:
- `GET /payroll` UI page
- payroll navigation entry
- paystub list view
- paystub detail / examination view
- readable presentation of header fields and payroll lines
- validation context
- approval / rejection affordances if Step 15 is complete first

Done when:
- payroll has a dedicated first-class UI surface instead of living only through APIs plus Review Queue detail

---

## Later, after Step 16

High-value later work can include:
- persisted review artifacts
- stronger scanned-PDF OCR
- stronger payroll line extraction
- portfolio UI
- richer allocation planning

---

## Current build priority summary

Do next in this order:
1. Step 14A
2. Step 14B
3. Step 14C
4. Step 14D
5. Step 14E
6. Step 15
7. Step 16

One-line summary:
First improve the shared shell and in-app upload experience, then implement payroll approval, then build the dedicated Payroll page.
