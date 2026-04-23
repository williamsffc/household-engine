# Household Engine

Local, privacy-first household financial command center — **FastAPI**, **SQLite**, and a small **Jinja2 + static JS** UI.

## What it is

- A **local-first hub**: one app, one database (`household.db`), shared **document upload**, **audit logging**, and **SQL views** for analytics.
- **Domain modules** on top of that hub: **Overview**, **Expenses**, **Payroll**, **Portfolio**, and **Review Queue** (each with HTML pages under `/` and JSON APIs under `/api/...`).
- Aimed at answering: **what came in**, **what went out**, **what needs review**, and how **cashflow / deployable surplus** look over time.

## UI routes

| Path | Purpose |
|------|---------|
| `/` | Overview — monthly cashflow, expense trends, forecast-style cards, portfolio summary hooks |
| `/expenses` | Expenses — upload (documents), ingest, monthly/category summaries, **transaction explorer** (range, filters, CSV export) |
| `/payroll` | Payroll — stubs / paystub pipeline (member-scoped documents, validation, review artifacts) |
| `/portfolio` | Portfolio — assumptions and trailing metrics (ties into overview-style data) |
| `/review-queue` | Review queue — items pending human review |

## API surface (high level)

| Prefix | Role |
|--------|------|
| `/api/overview` | Overview analytics (cashflow, expenses series, portfolio snippets, etc.) |
| `/api/expenses` | Monthly/category/recent summaries, **transactions** list, **ingest** for expense documents |
| `/api/documents` | Upload and register files (`module_owner`: e.g. `expenses`, `payroll`) |
| `/api/payroll` | Payroll ingest, validation, member-scoped flows |
| `/api/review-queue` | Review queue read/update paths |
| `/api/household` | Household metadata |
| `/health` | Liveness |

OpenAPI: `http://127.0.0.1:8000/docs` (when the server is running).

## Project layout

```
household-engine/
├── config/              # YAML for expenses rules/categories/accounts (ingest + categorization)
├── data/               # Runtime uploads & exports (gitignored patterns — see .gitignore)
├── docs/               # architecture.md, handoff notes
├── migrations/         # Ordered SQL migrations → household.db
├── src/
│   ├── api/            # FastAPI routers
│   ├── core/           # DB, settings, security (local-only middleware), logging, file store
│   ├── expenses/       # Parsers, ingest, categorizer, anomalies, repository
│   ├── payroll/        # Normalizer, PDF/OCR extractors, validator, repository
│   ├── services/       # Documents, audit, analytics, portfolio, review_queue, optional LLM hooks
│   ├── models/, schemas/
│   ├── templates/, static/
│   └── main.py
├── tests/
├── requirements.txt
└── run.py               # uvicorn dev entry (reload)
```

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

Dev shortcut (reload on code changes):

```powershell
python run.py
```

Then open **http://127.0.0.1:8000/** (Overview). Other pages: `/expenses`, `/payroll`, `/portfolio`, `/review-queue`.

**Dependencies** (see `requirements.txt`): FastAPI, uvicorn, pandas, PyYAML, pdf / spreadsheet / image tooling for document pipelines.

## Configuration & data

- **Database**: `household.db` at the repo root (created on startup; migrations applied automatically).
- **Expenses ingest** reads shared YAML under `config/` (`categories.yaml`, `rules.yaml`, `accounts.yaml`) — same conceptual model as a standalone recon pipeline, integrated here.
- **Uploaded files** land under `data/` (raw / staging / processed / rejected / exports as ensured in `main.py` startup).

## Privacy / local-first

- Intended to run **on your machine**; uploads and the DB stay local unless you copy them elsewhere.
- Sensitive paths are **gitignored** by default (`data/`, `*.db`, etc.).
- **Non-loopback requests are rejected** unless you set `HOUSEHOLD_ALLOW_REMOTE=1` (use only if you intentionally want LAN access).

## Testing

```powershell
python -m pytest tests/
```

Some test modules are thin placeholders; coverage grows with the modules.

## Documentation

- **`docs/architecture.md`** — hub-and-spoke blueprint, household vs member model, UI direction.
- **`docs/handoff.md`** — session / handoff context when present.

## Status

This is **active V1 / incremental** work: behavior and schema evolve with migrations. For deeper design intent, start with `docs/architecture.md`; for code entry points, `src/main.py` and `src/api/`.
