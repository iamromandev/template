"""Timing middleware.

Adds ``X-Response-Time`` header in milliseconds. Cheap; runs on every
request but only a single ``time.perf_counter`` pair.
"""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

RESPONSE_TIME_HEADER = "X-Response-Time"


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        start = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        response.headers[RESPONSE_TIME_HEADER] = f"{elapsed_ms:.2f}ms"
        return response
