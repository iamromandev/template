"""Prometheus metrics — minimal hand-rolled setup.

Why hand-rolled vs ``prometheus-fastapi-instrumentator``?
    * One fewer dep; full control over label cardinality.
    * The default instrumentator labels can explode cardinality with
      high-cardinality paths (e.g. ``/users/{uuid}``).
    * We expose only what we actually use: HTTP requests, request
      duration, errors, plus a few business signals.

Mounted at ``/metrics`` (text format 0.0.4). Skip logging ``/metrics``
itself via ``LoggingMiddleware._skip_paths``.
"""

from __future__ import annotations

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

# Standard HTTP metrics — single Histogram with sensible buckets.
HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Count of HTTP requests handled.",
    labelnames=("method", "path", "status"),
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    labelnames=("method", "path", "status"),
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Business signal example — count successful logins. Add more as needed.
AUTH_LOGIN_SUCCESS_TOTAL = Counter(
    "auth_login_success_total",
    "Count of successful logins.",
)


def render_metrics() -> tuple[bytes, str]:
    """Return ``(body, content_type)`` for the ``/metrics`` endpoint."""
    return generate_latest(), CONTENT_TYPE_LATEST


__all__ = [
    "AUTH_LOGIN_SUCCESS_TOTAL",
    "HTTP_REQUESTS_TOTAL",
    "HTTP_REQUEST_DURATION_SECONDS",
    "render_metrics",
]
