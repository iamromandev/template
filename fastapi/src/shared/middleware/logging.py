"""Structured access logging middleware.

Logs one line per request with: method, path, status, duration_ms,
request_id, client_ip. Skips ``/metrics`` and ``/health/check`` to
avoid recursive spam.
"""

from __future__ import annotations

import time

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

_SKIP_PATHS = frozenset({"/metrics", "/health/check"})


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, *, skip_paths: frozenset[str] | None = None) -> None:
        super().__init__(app)
        self._skip_paths = skip_paths or _SKIP_PATHS

    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        path = request.url.path
        if path in self._skip_paths:
            return await call_next(request)

        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        request_id = getattr(request.state, "request_id", "-")
        client_ip = request.client.host if request.client else "-"
        logger.bind(
            request_id=request_id,
            method=request.method,
            path=path,
            status=response.status_code,
            duration_ms=f"{elapsed_ms:.2f}",
            client_ip=client_ip,
        ).info("http_access")
        return response
