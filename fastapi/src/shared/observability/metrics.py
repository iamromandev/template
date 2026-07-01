"""Prometheus metrics endpoint + per-request instrumentation."""

from __future__ import annotations

import time

from fastapi import APIRouter, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.config.config import Settings, get_settings
from src.shared.observability import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
    render_metrics,
)

router = APIRouter()


@router.get(path="/metrics", include_in_schema=False)
async def metrics() -> Response:
    body, content_type = render_metrics()
    return Response(content=body, media_type=content_type)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Records per-request latency + counter on the response.

    Skips ``/metrics`` itself to avoid noise. Uses
    ``request.scope.get('route').path`` for the templated path
    (e.g. ``/api/v1/users/{user_id}``) instead of the raw URL — keeps
    Prometheus label cardinality bounded.
    """

    def __init__(self, app, *, enabled: bool | None = None) -> None:
        super().__init__(app)
        settings: Settings = get_settings()
        self._enabled = enabled if enabled is not None else settings.metrics_enabled

    async def dispatch(self, request, call_next):  # type: ignore[override]
        if not self._enabled or request.url.path == "/metrics":
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        elapsed = time.perf_counter() - start

        route = request.scope.get("route")
        path = getattr(route, "path", request.url.path)
        labels = (request.method, path, str(response.status_code))
        HTTP_REQUESTS_TOTAL.labels(*labels).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(*labels).observe(elapsed)
        return response


__all__ = ["PrometheusMiddleware", "router"]
