# Step 13 — Advanced Hardening / V2

Completed.

### Chosen hardening targets

This step intentionally chose a **small, high-value subset** of deferred V2 work:

1. richer document review UX
2. modest stronger local-network controls

These were chosen because they fit the current repo state, improve trust/usability, and avoid broad redesign or misleading semantics.

### Implemented

#### Review Queue UX

* `GET /review-queue` UI page
* `src/templates/review_queue.html`
* `static/js/review_queue.js`
* `src/api/routes_ui.py` updated to serve the Review Queue page
* `src/templates/base.html` updated with Review Queue navigation

#### Local-only guardrail

* `src/core/settings.py`
* `src/core/security.py`
* `src/main.py` updated to wire local-only middleware

### Behavior

#### Review Queue UX

* the Review Queue now has a usable read-only UI
* it consumes the existing backend review APIs:

  * `GET /api/review-queue`
  * `GET /api/review-queue/{document_id}`
* the page allows a user to:

  * see pending `in_review` documents
  * click an item
  * view redacted text
  * view redaction counts
  * view validation warnings
  * view draft paystub and draft lines

#### Local-only guardrail

* by default, the app rejects non-loopback requests with a 403 JSON response
* this is a local-first guardrail, not a full auth system
* intentional override is available via:

  * `HOUSEHOLD_ALLOW_REMOTE=1`

### Important Step 13 notes

* approve/reject workflow was still intentionally deferred
* visual PDF redaction was still intentionally deferred
* field-level confidence scoring was still intentionally deferred
* this step focused on selective hardening, not broad V2 sprawl

### Result

The system now has:

* a usable Review Queue UI on top of the existing backend review path
* a modest local-network guardrail aligned with the project’s local-first design

This completes the roadmap as currently defined.

---

## Current Implemented Routes

### UI

* `GET /`
* `GET /expenses`
* `GET /review-queue`

### Overview API

* `GET /api/overview/summary`
* `GET /api/overview/recent-documents`
* `GET /api/overview/cashflow`
* `GET /api/overview/trends`
* `GET /api/overview/forecast`
* `GET /api/overview/portfolio`

### Expenses API

* `GET /api/expenses/transactions`
* `GET /api/expenses/monthly`
* `GET /api/expenses/categories`
* `GET /api/expenses/recent`
* `POST /api/expenses/documents/{document_id}/ingest`

### Payroll API

* `POST /api/payroll/documents/{document_id}/ingest`
* `GET /api/payroll/paystubs`
* `GET /api/payroll/paystubs/{paystub_id}`
* `GET /api/payroll/monthly`

### Review Queue API

* `GET /api/review-queue`
* `GET /api/review-queue/{document_id}`

---

## What Is Not Implemented Yet

### Payroll

* no approve/reject payroll workflow yet
* no canonical payroll approval flow yet
* no robust scanned-PDF OCR yet
* no strong payroll line-item extraction yet
* no payroll member trend routes yet

### Review queue

* no approve endpoint yet
* no reject endpoint yet
* no persisted redacted review payload yet

### Portfolio / V2

* no portfolio UI yet
* no brokerage integrations
* no richer allocation planning layer
* no balance-aware surplus model

### Deferred advanced items

* no visual PDF redaction
* no field-level extraction confidence
* no full auth / user-role system
* no broader advanced anomaly scoring yet

---

## Project status

The project is now:

* **V1-complete**
* plus **selective V2-ready hardening**

Core outcomes achieved:

* local-first shared Hub
* working Expenses spoke
* working Payroll draft/review-oriented spoke
* shared analytics and cashflow views
* Overview UI
* Expenses UI
* Review Queue UI
* modest trend / forecast layer
* modest portfolio / deployable-surplus layer
* selective hardening without uncontrolled V2 sprawl
