from __future__ import annotations

from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


def _is_loopback(host: str | None) -> bool:
    if not host:
        return False
    h = host.strip().lower()
    return h in {"127.0.0.1", "localhost", "::1"}


class LocalOnlyMiddleware(BaseHTTPMiddleware):
    """Best-effort local-network hardening.

    This is not "auth". It is a guardrail: by default, only loopback clients can call the app.
    """

    def __init__(self, app, *, allow_remote: bool) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._allow_remote = bool(allow_remote)

    async def dispatch(self, request: Request, call_next: Callable[[Request], Response]) -> Response:
        if self._allow_remote:
            return await call_next(request)

        client_host = getattr(getattr(request, "client", None), "host", None)
        if _is_loopback(client_host):
            return await call_next(request)

        return JSONResponse(
            status_code=403,
            content={
                "detail": "Remote requests are disabled (local-first). Set HOUSEHOLD_ALLOW_REMOTE=1 to allow non-loopback clients.",
                "client_host": client_host,
            },
        )
