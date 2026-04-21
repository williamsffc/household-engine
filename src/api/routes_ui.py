from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

from src.core.database import get_repo_root


router = APIRouter(tags=["ui"])

templates = Jinja2Templates(directory=str(get_repo_root() / "src" / "templates"))
# Work around an upstream caching interaction on some environments where
# template globals make cache keys unhashable. Disabling caching is fine for V1.
templates.env.cache = None  # type: ignore[attr-defined]


@router.get("/")
def overview_page(request: Request):
    # Starlette's Jinja2Templates signature is (request, name, context).
    return templates.TemplateResponse(request, "overview.html", {"request": request})


@router.get("/expenses")
def expenses_page(request: Request):
    return templates.TemplateResponse(request, "expenses.html", {"request": request})


@router.get("/review-queue")
def review_queue_page(request: Request):
    return templates.TemplateResponse(request, "review_queue.html", {"request": request})

