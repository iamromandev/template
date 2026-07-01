"""Cross-cutting middleware.

Mount order (outermost-first in FastAPI):
    1. ``RequestIdMiddleware``      — assigns / propagates X-Request-ID
    2. ``ErrorBoundaryMiddleware``  — last-resort catch before global handler
    3. ``TimingMiddleware``         — records X-Response-Time
    4. ``LoggingMiddleware``        — structured access log

CORSMiddleware is mounted by ``main.create_app()`` from settings, and
sits between TimingMiddleware and the app (Starlette applies middleware
in reverse-include order, so order matters — set in main.py).
"""

from __future__ import annotations

from src.shared.middleware.error_boundary import ErrorBoundaryMiddleware
from src.shared.middleware.logging import LoggingMiddleware
from src.shared.middleware.request_id import RequestIdMiddleware
from src.shared.middleware.timing import TimingMiddleware

__all__ = [
    "ErrorBoundaryMiddleware",
    "LoggingMiddleware",
    "RequestIdMiddleware",
    "TimingMiddleware",
]
