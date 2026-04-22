from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.routes_documents import router as documents_router
from src.api.routes_expenses import router as expenses_router
from src.api.routes_household import router as household_router
from src.api.routes_health import router as health_router
from src.api.routes_overview import router as overview_router
from src.api.routes_payroll import router as payroll_router
from src.api.routes_review import router as review_router
from src.api.routes_ui import router as ui_router
from src.core.database import init_db, get_repo_root
from src.core.security import LocalOnlyMiddleware
from src.core.settings import get_settings


def _ensure_dirs() -> None:
    repo_root = get_repo_root()
    for relative_path in [
        Path("data/raw"),
        Path("data/staging"),
        Path("data/processed"),
        Path("data/rejected"),
        Path("data/exports"),
    ]:
        (repo_root / relative_path).mkdir(parents=True, exist_ok=True)


app = FastAPI(title="Household Engine", version="0.1.0")
settings = get_settings()
app.add_middleware(LocalOnlyMiddleware, allow_remote=settings.allow_remote)

repo_root = get_repo_root()
app.mount("/static", StaticFiles(directory=str(repo_root / "static")), name="static")


@app.on_event("startup")
def on_startup() -> None:
    _ensure_dirs()
    init_db()


app.include_router(health_router)
app.include_router(documents_router)
app.include_router(expenses_router)
app.include_router(household_router)
app.include_router(overview_router)
app.include_router(payroll_router)
app.include_router(review_router)
app.include_router(ui_router)