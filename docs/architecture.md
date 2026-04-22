# Household Engine — Architecture Blueprint (Updated)

## Purpose of this document

This file is the **long-term blueprint / target design** for Household Engine.

It should describe:
- the intended product shape
- the durable architectural boundaries
- the UI / data / workflow principles the repo should converge toward
- the next major platform capabilities expected over time

It should **not** be treated as the source of truth for what is already implemented.
For current implemented state, use `handoff.md`.
For the immediate next build slice, use `Pasted_text.md`.

---

## Product vision

Household Engine is a **local-first, privacy-first household finance command center** built on a Hub-and-Spoke architecture.

The product should help answer, in one place:
- what came in
- what went out
- what is pending review
- what has been approved as canonical
- what is changing over time
- what modest deployable surplus is available

The system is designed first for **single-household local use**, with modest local network controls, simple reviewability, and clear module boundaries.

---

## Architectural model

### Hub responsibilities

The Hub owns shared platform concerns:
- FastAPI application shell
- SQLite database and migrations
- document intake and registry
- processing lifecycle and audit logging
- review queue orchestration
- shared analytics views
- shared UI shell
- theme system and responsive navigation
- reusable upload interaction surfaces

### Spoke responsibilities

Each module owns its domain logic:
- **Expenses**: ingest, transaction normalization, categorization, analytics, dashboard UX
- **Payroll**: paystub ingest, extraction, validation, review, approval lifecycle, paystub examination UX
- **Portfolio**: later, surplus interpretation and planning UI

The design goal is that the Hub provides stable infrastructure and the Spokes provide domain-specific workflows without leaking implementation details across modules.

---

## Current product shape the architecture should support

The architecture should support four user-facing areas:
- **Overview** — command center dashboard
- **Expenses** — expense dashboard and expense document intake
- **Payroll** — paystub examination, payroll history, approval-oriented workflow
- **Review Queue** — cross-document review surface focused first on payroll drafts

The Hub should also support common cross-page behavior:
- theme switching between light and dark mode
- responsive navigation that never disappears
- reusable drag-and-drop / click-to-upload interactions
- consistent card, table, chart, and empty-state patterns

---

## UI architecture principles

### 1. The app should be interacted with through the UI, not through folder conventions

Even though the product is local-first, users should primarily work through app surfaces rather than manually managing folder structure.

That means:
- upload should be available in-page where the workflow begins
- document status should be visible in the UI
- ingest / review / approval should be driven by app actions
- route-level flows should feel productized rather than developer-oriented

### 2. Shared shell first, page-specific features second

Before adding many more screens, the shell should provide:
- stable page layout
- responsive navigation
- semantic theme tokens
- clear active-page state
- reusable page headers
- shared alert / status / loading patterns

### 3. Light mode and dark mode are both first-class

The app should support:
- a default light theme
- an optional dark theme
- locally persisted theme preference
- semantic color tokens rather than hardcoded per-page colors

Recommended semantic token groups:
- app background
- card / panel surface
- elevated surface
- border subtle / strong
- text primary / secondary / muted
- accent
- success / warning / error / info
- chart-safe palette mappings

### 4. Responsive behavior should degrade gracefully

Navigation should never disappear.

Recommended behavior:
- **large screens**: full sidebar with labels
- **medium screens**: collapsed icon rail with active-state emphasis
- **small screens**: top bar with menu drawer or similarly compact navigation

### 5. Reusable upload components should be shared across modules

The product should use a common upload surface pattern with:
- drag-and-drop
- click-to-upload fallback
- accepted file hints
- upload state feedback
- processing / success / failure messaging

This shared component should be usable in:
- Expenses
- Review Queue
- Payroll page later

---

## Data and workflow architecture

### Shared document lifecycle

The shared `documents.status` lifecycle should remain explicit:
- `uploaded`
- `processing`
- `in_review`
- `approved`
- `rejected`
- `error`

This lifecycle is a platform concern, not a page concern.

### Payroll lifecycle principle

Payroll is review-driven and should remain so.

Architecture rule:
- payroll draft extraction is **not canonical**
- only approved payroll contributes to household analytics
- review queue and payroll page should expose the same canonical review state

A durable payroll workflow should be:
1. upload payroll document
2. register document
3. extract / scrub / validate
4. persist draft paystub + draft lines
5. surface in Review Queue and Payroll UI
6. approve or reject
7. only then include in payroll analytics and cross-module cashflow views

### Review artifact direction

Persisted review artifacts are still a valid medium-term design target.

That can later include:
- persisted review payload snapshots
- structured validation results
- approval / rejection metadata
- reviewer action history

But the architecture should keep this additive, not required for the current immediate slice.

---

## Durable backend boundaries

### Core / shared platform

`src/core/` should own only shared infrastructure concerns such as:
- settings
- database
- security / local-only policy
- storage paths
- hashing
- shared status constants
- generic exceptions

### API layer

`src/api/` should own thin HTTP route handlers only.
Route handlers should delegate to services or modules and avoid embedding business logic.

### Services layer

`src/services/` should own cross-module services such as:
- document registry
- audit logging
- analytics orchestration
- review queue platform operations
- shared upload orchestration if a cross-module upload service is introduced

### Expense domain

`src/expenses/` should own expense-only logic such as:
- statement parsers
- normalization
- categorization
- anomaly checks
- repository access
- expense-specific presentation shaping if needed

### Payroll domain

`src/payroll/` should own payroll-only logic such as:
- native text extraction
- OCR fallback
- PII scrubbing
- structured extraction normalization
- deterministic validation
- approval / rejection domain transitions
- payroll repository access
- payroll page read models if needed

---

## UI structure target

### Overview

Purpose:
- command center dashboard
- summary cards
- recent documents
- pending review counts
- monthly cashflow / trends / forecast context

### Expenses

Purpose:
- expense upload surface
- recent expense document activity
- category and monthly views
- transaction exploration
- future tighter intake-to-analysis experience

### Payroll

Purpose:
- dedicated paystub examination page
- paystub list and detail views
- readable header + line-item presentation
- validation and draft review context
- approval / rejection actions once the approval workflow exists

### Review Queue

Purpose:
- cross-document review area focused first on payroll drafts
- pending item list
- redacted text review
- validation warning review
- draft payload inspection
- path to approval / rejection

Payroll and Review Queue should complement each other:
- Review Queue = triage and queue surface
- Payroll = payroll-focused record and examination surface

---

## Analytics architecture principles

UI pages should continue reading from stable API/view layers rather than assembling important financial meaning entirely in the browser.

Important rule to preserve:
- only approved payroll counts toward shared analytics, forecasting, and deployable-surplus calculations

This keeps overview outputs honest during draft / in-review states.

---

## Theme system guidance

The revised UI direction should feel:
- calmer
- lighter
- more legible
- less terminal-like
- still structured and data-oriented

Preferred baseline:
- light mode as default
- dark mode optional
- soft neutral backgrounds
- white or near-white cards in light mode
- restrained borders and shadows
- muted status colors rather than harsh saturation

The architecture should avoid hardcoded visual assumptions at the page level.
All pages should consume shared theme variables/tokens.

---

## Near-term architectural roadmap

The next platform-focused sequence the architecture should support is:

1. **Theme system + shell foundation**
   - semantic tokens
   - light/dark mode toggle
   - persisted theme preference
   - shared page shell cleanup

2. **Responsive navigation overhaul**
   - full sidebar on large screens
   - collapsed icon navigation on medium screens
   - compact navigation on small screens

3. **Shared in-app upload interaction layer**
   - reusable upload component
   - plug into Expenses and Review Queue first

4. **Expenses UX refresh**
   - integrate upload directly into the page
   - align cards/charts/tables with the shared theme system

5. **Review Queue UX refresh**
   - integrate payroll upload entry point
   - improve hierarchy and validation display

6. **Payroll approval / canonical workflow**
   - approve/reject actions
   - canonical analytics inclusion behavior
   - audit semantics for decisions

7. **Dedicated Payroll page / paystub examination UI**
   - payroll-focused inspection and history surface

8. **Persisted review artifacts and stronger OCR**
   - follow after the approval path is stable

---

## Long-term direction beyond the immediate slice

After the shell, upload, review, and payroll approval path are solid, later work can still include:
- portfolio UI
- richer surplus interpretation
- stronger scanned-PDF OCR
- stronger payroll line extraction
- persisted review artifacts
- broader local-network controls / auth hardening
- selective parser expansion

---

## One-line architecture summary

Household Engine should evolve into a local-first household finance command center with a stable shared Hub, reusable themed UI shell, in-app document workflows, review-driven payroll approval, and modular domain pages for Expenses, Payroll, Review Queue, and later Portfolio.
