## Household Engine

Local, privacy-first household financial command center.

### What this is

- **Local-first** FastAPI + SQLite “Hub” with domain modules (Expenses, Payroll, Portfolio).
- Designed to answer: **what came in**, **what went out**, and (eventually) **what surplus is deployable**.

### Privacy / local-first note

- This repo is intended to run **locally**.
- Uploaded documents and the local database are **ignored by default** via `.gitignore` (see `data/` and `*.db`).
- By default, the app rejects non-loopback requests. Set `HOUSEHOLD_ALLOW_REMOTE=1` only if you intentionally want LAN access.

### Dev quickstart

See `docs/architecture.md` for the full blueprint. Current implemented modules include:

- **Overview**: `GET /` UI + `/api/overview/*` endpoints (cashflow, trends, forecast, portfolio summary)
- **Expenses**: `GET /expenses` UI + `/api/expenses/*`
- **Payroll**: draft ingest + `/api/payroll/*` (approved-only analytics views exist; approval workflow is not implemented yet)
- **Review Queue**: `GET /review-queue` UI + `/api/review-queue/*` (read path)

### Run

```powershell
python -m pip install -r requirements.txt
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Then open:

- `http://127.0.0.1:8000/` (Overview)
- `http://127.0.0.1:8000/expenses` (Expenses)
- `http://127.0.0.1:8000/review-queue` (Review Queue)
