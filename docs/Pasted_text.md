# Step 18 — Review Artifact + Payroll Quality Improvements

Current active step.

## Context

Household Engine is complete through Step 17 and is now best described as:

* V1-complete
* plus selective V2-ready hardening
* plus post-roadmap UI foundation refresh
* plus canonical payroll approval workflow
* plus dedicated Payroll page / paystub examination UI
* plus better household-member selection UX

The app currently has:

* local-first FastAPI + SQLite Hub
* working Expenses ingest, analytics, and UI
* working Payroll draft ingest, payroll APIs, and review queue backend/UI
* shared cashflow analytics, trends, forecast, and portfolio summary endpoints
* Overview, Expenses, Review Queue, and Payroll UI pages
* shared shell/theme foundation
* responsive shared navigation
* shared in-app upload component
* Expenses UX refresh
* Review Queue UX refresh
* payroll approve/reject + canonical approval flow
* dedicated Payroll page with household-vs-person browsing
* improved member picker UX for payroll upload

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
* coherent state transitions across:
  * `documents.status`
  * `payroll_paystubs.status`
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
* status clarity across:
  * approved
  * rejected
  * in_review
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

## Product rule now locked in

The app is **household-first**, but every payroll record belongs to exactly **one household member**.

That means:

* payroll documents/paystubs are tracked per person
* approved payroll analytics must work both:
  * per person
  * household combined
* household totals are the rollup of approved per-member payroll
* upload/review/approval flow must preserve ownership truthfully

## Goal of Step 18

Improve the quality, durability, and usefulness of payroll review artifacts and payroll extraction outputs without broadening into a major redesign.

This step is about making the review/examination pipeline more trustworthy and useful over time.

## Product intent

Right now the payroll workflow exists and is usable, but some quality-oriented pieces are still thin:

* review artifacts are mostly transient/read-through payloads
* rejection reasons live only in audit log details
* payroll lines can be sparse
* scanned-PDF/OCR robustness is still limited
* extraction quality can still be improved

This step should improve the practical reliability of payroll handling while staying incremental.

## Required outcome

Improve payroll review artifact and payroll quality behavior with focus on:

1. better persisted review artifact support where practical
2. stronger payroll detail capture/readability where practical
3. improved payroll extraction quality or fallback robustness
4. better traceability of review outcomes where practical
5. no regression to approval/canonical workflow
6. no regression to household-member ownership model

## Scope guidance

This is a quality-improvement step, not a broad architecture rewrite.

That means:

* improve what happens around payroll review artifacts and extraction quality
* make small, high-value persistence/traceability improvements if practical
* improve payroll quality where the current implementation is thin
* keep the implementation incremental and aligned with the current repo
* do not broaden into portfolio work
* do not redesign the whole app
* do not start advanced auth/settings systems

## Suggested focus areas

### Review artifact persistence

Today some review information is available only transiently or indirectly.

Consider modest improvements such as:

* preserving rejection reason more explicitly if practical
* preserving useful review payload details more durably if practical
* improving traceability of what was reviewed/approved/rejected

### Payroll detail quality

Improve practical payroll usefulness where current outputs are thin:

* better payroll line handling if low-risk
* clearer draft/approved detail completeness
* small improvements to extraction robustness

### OCR / scanned-document fallback quality

If there is a modest improvement that increases scanned-paystub resilience without sprawling, this is a good place for it.

### Review/payload honesty

The system should remain honest about what is known vs inferred vs missing.

## Files likely involved

Review first:

* `src/payroll/ingest.py`
* `src/payroll/extractor_pdf.py`
* `src/payroll/extractor_ocr.py`
* `src/payroll/repository.py`
* `src/services/review_queue.py`
* `src/api/routes_review.py`
* migrations / schema files if modest persistence changes are needed
* `src/templates/review_queue.html`
* `src/templates/payroll.html`
* `static/js/review_queue.js`
* `static/js/payroll.js`

## Deliverables for this step

1. improved payroll review artifact handling and/or persistence
2. improved payroll quality/reliability in at least one high-value area
3. better traceability of review outcomes where practical
4. no regression to approval/canonical workflow
5. no regression to member ownership semantics
6. no regression to current Review Queue / Payroll page UX

## Constraints

* keep changes incremental
* no framework migration
* no Tailwind rewrite
* no unrelated global redesign
* no portfolio work yet
* no advanced auth/settings system yet
* keep the system local-first and honest about data quality/state

## What comes next after Step 18

If Step 18 lands cleanly, the next roadmap order becomes:

* Step 19 — Portfolio UI and richer household planning