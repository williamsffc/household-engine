# Step 24 — Scanned-PDF OCR Support

Current active step.

## Context

Household Engine is complete through Step 23 and is now best described as:

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

## Step 14A–23 status

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

## Product rule now locked in

The app is **household-first**.

That means:

* household cashflow and planning remain the top-level view
* payroll and documents still belong to specific household members
* approved payroll remains the only payroll that affects analytics/planning
* OCR support must preserve ownership, review honesty, and approval semantics
* OCR-extracted drafts should still remain review-driven and honest about quality limits

## Goal of Step 24

Add scanned-PDF OCR support so payroll ingestion can still produce a reviewable draft when native PDF text extraction is missing or insufficient.

This step should broaden payroll intake coverage while keeping the workflow conservative and review-based.

## Product intent

Right now payroll ingestion works best when native PDF text is available.

This step should support cases where:

* a paystub PDF is scanned or image-like
* pdfplumber returns little or no usable text
* the current native-text path fails too early

The goal is not perfect OCR.  
The goal is to produce a modest, reviewable draft rather than a dead end.

## Required outcome

Add OCR support for scanned payroll PDFs with focus on:

1. detecting when native text is missing or insufficient
2. invoking OCR fallback in a contained, honest way
3. feeding OCR text into the same existing extraction/review path where practical
4. preserving ownership, review, and approval semantics
5. signaling clearly when OCR fallback was used
6. avoiding false confidence about OCR quality

## Scope guidance

This is an OCR fallback step, not a document-intelligence rewrite.

That means:

* add a modest OCR fallback path
* keep the downstream extraction/review pipeline consistent where possible
* make OCR usage visible in artifacts/review payloads
* keep the system honest about quality limitations
* do not broaden into advanced visual annotation/redaction
* do not redesign the whole payroll pipeline
* do not weaken review-driven approval semantics

## Suggested focus areas

### OCR fallback trigger

Handle cases where native PDF text is:

* empty
* too sparse
* clearly unusable for payroll extraction

The trigger should be conservative and explainable.

### OCR text integration

Feed OCR text into the existing extraction path as much as possible so:

* field extraction
* payroll lines
* validation
* review payloads

continue to behave consistently.

### OCR visibility

Make sure the system captures and surfaces when OCR was used, for example in:

* document metadata
* review artifact metadata
* review/payload/UI hints if already supported

### Honesty

OCR-backed results should remain draft-level and review-oriented.  
The UI and payloads should not imply that OCR is as trustworthy as high-quality native text.

## Files likely involved

Review first:

* `src/payroll/ingest.py`
* `src/payroll/extractor_pdf.py`
* `src/payroll/extractor_ocr.py`
* `src/payroll/review_artifacts.py`
* `src/api/routes_review.py`

Potentially inspect:

* document metadata / ocr_used handling
* review payload composition
* any current OCR helper implementation already present but underused

## Deliverables for this step

1. scanned-PDF OCR fallback for payroll ingest
2. conservative trigger for OCR usage
3. OCR text feeding into the existing extraction/review path
4. honest metadata/signaling when OCR is used
5. no regression to approval/canonical workflow
6. no regression to member-aware payroll model
7. no regression to approved-only analytics semantics

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no visual PDF annotation/redaction system
* no unrelated global redesign
* keep the system local-first and honest about OCR quality/state

## What comes next after Step 24

After Step 24, the next roadmap order becomes:

* Step 25 — Reopen / undo workflow for payroll decisions

Additional later work can still include:
* richer review artifact expansion
* further payroll extraction quality improvements