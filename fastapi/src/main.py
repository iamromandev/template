"""Application factory — wires middleware, routes, observability, errors.

Layered top-to-bottom (FastAPI applies middleware in reverse-include order):

    LoggingMiddleware (outermost)
      └── TimingMiddleware
            └── RequestIdMiddleware
                  └── CORSMiddleware (only if origins configured)
                        └── ErrorBoundaryMiddleware (innermost)
                              └── routes / metrics
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import configure_logging, get_settings
from src.core.common import get_app_version
from src.core.error import init_global_errors
from src.data.db import init_db
from src.module.health.route import router as _health_router
from src.module.user.route import router as _user_router
from src.shared.middleware.error_boundary import ErrorBoundaryMiddleware
from src.shared.middleware.logging import LoggingMiddleware
from src.shared.middleware.request_id import RequestIdMiddleware
from src.shared.middleware.timing import TimingMiddleware
from src.shared.observability.metrics import PrometheusMiddleware
from src.shared.observability.metrics import router as metrics_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="FastAPI Template",
        description="Standard production-ready FastAPI template.",
        version=get_app_version(),
        debug=settings.debug,
        lifespan=lifespan,
    )

    # Order matters — FastAPI applies last-added first.
    app.add_middleware(ErrorBoundaryMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIdMiddleware)
    if settings.cors_origin_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origin_list,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.add_middleware(PrometheusMiddleware, enabled=settings.metrics_enabled)

    # Global error handlers — must be registered before init_db so its
    # own exception handlers compose with ours.
    init_global_errors(app)

    # Routes: versioned API + Prometheus scrape endpoint.
    _router = APIRouter(prefix="/api/v1")
    _router.include_router(_health_router)
    _router.include_router(_user_router)
    app.include_router(_router)
    app.include_router(metrics_router)

    # Tortoise ORM — registers its own startup/shutdown with `app.lifespan`.
    init_db(app)
    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        loop="uvloop",
    )
