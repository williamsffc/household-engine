# Step 26 — Targeted Payroll Extraction Follow-Ups

Current active step.

## Context

Household Engine is complete through Step 25 and is now best described as:

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

## Step 14A–25 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* extraction improvements must preserve review honesty and member ownership
* reopened/OCR-backed drafts are opportunities to improve quality, not hide uncertainty

## Goal of Step 26

Make targeted, practical payroll extraction improvements based on the current weak spots that still show up in native-text and OCR-backed drafts.

This step should be selective and high-value, not a broad parser rewrite.

## Product intent

Now that the system supports:

* better native extraction
* OCR fallback
* reopen / re-review

the next best move is to tighten the most common extraction rough edges, especially around:

* line classification
* noisy OCR text patterns
* awkward label normalization
* partial draft usefulness

The goal is better drafts, not fake certainty.

## Required outcome

Improve payroll extraction in a modest, targeted way with focus on:

1. better line classification for common payroll row types
2. better cleanup/normalization of noisy extracted labels
3. practical improvements for OCR-backed drafts where low-risk
4. fewer obviously wrong or junk rows
5. no regression to review honesty
6. no regression to approval/canonical workflow
7. no regression to member-aware payroll semantics

## Scope guidance

This is a targeted extraction refinement step, not a parser-platform rewrite.

That means:

* improve weak spots that are already visible in current drafts
* prefer common-case wins over broad complexity
* keep heuristics understandable
* keep warnings/review semantics honest
* do not start unrelated UI redesign
* do not introduce fake confidence scoring
* do not change approved-only analytics semantics

## Suggested focus areas

### Line classification refinement

Improve category assignment for rows such as:

* taxes
* deductions
* regular earnings
* reimbursements / adjustments
* employer-specific wording that is currently miscategorized too often

### Label normalization

Reduce noise from OCR/native extraction such as:

* duplicated punctuation
* broken spacing
* common OCR artifacts
* common payroll abbreviations that can be normalized safely

### OCR-friendly cleanup

Add modest improvements that help OCR-backed text without pretending OCR is perfect, for example:

* filtering obvious OCR junk rows
* handling common OCR substitutions where low-risk
* improving matching on noisy but recoverable labels

### Review honesty

Keep the draft review model intact:
* better extraction where possible
* still clear when rows/fields remain uncertain or missing

## Files likely involved

Review first:

* `src/payroll/ingest.py`
* `src/payroll/normalizer.py`
* `src/payroll/validator.py`

Potentially inspect:

* OCR-related text flow in:
  * `src/payroll/payroll_text_extract.py`
  * `src/payroll/extractor_ocr.py`
* current review/payload rendering in:
  * `static/js/review_queue.js`
  * `static/js/payroll.js`

## Deliverables for this step

1. targeted payroll extraction refinements
2. better line classification and/or label cleanup
3. modest OCR-friendly cleanup where practical
4. no regression to review honesty
5. no regression to approval/canonical workflow
6. no regression to member-aware payroll model

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no full parser rewrite
* no fake confidence scoring
* no unrelated global redesign
* keep the system local-first and honest about data quality/state

## What comes next after Step 26

After Step 26, the next work should be chosen based on the highest practical value, likely from:

* richer review artifact expansion
* additional payroll-quality refinement
* command-center polish based on real usage