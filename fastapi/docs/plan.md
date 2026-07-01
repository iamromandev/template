# FastAPI Production Template — Architecture Plan

> **Role:** Senior Software Architect  
> **Project:** `fastapi-template` — Standard Production-Ready FastAPI Project Structure  
> **Version:** 1.0.0  
> **Last Updated:** 2025-07-01

---

## 1. Executive Summary

This document defines the target architecture for a **standard, production-grade FastAPI project template**. It is derived from a thorough analysis of the existing codebase (`fastapi-template` v0.0.1) and adopts its proven patterns while expanding into a comprehensive, enterprise-ready structure.

### 1.1 Current State Assessment

The existing codebase is a **well-architected minimal starter** with the following strengths:

| Strength | Description |
|----------|-------------|
| **Clean 4-Tier Architecture** | Route → Service → Repo → Model with clear separation of concerns |
| **Module-Centric Layout** | Domain modules are self-contained — `src/health/` owns its own route/service/repo/schema/model. Easy to delete, extract, or move to a microservice. |
| **Robust Base Abstractions** | `Base` / `LinkBase` (Tortoise), `BaseRepo[M]`, `BaseSchema`, `BaseService` |
| **Unified Response Envelope** | `Success[T]` and `Error` classes provide consistent API responses |
| **Type-Safe Enums** | `Status`, `ErrorType`, `Code` — exhaustive, HTTP-standard aligned |
| **Global Error Handling** | Custom exception handlers for `HTTPException`, `RequestValidationError`, `Error`, and catch-all `Exception` |
| **Modern Tooling** | `uv` (package manager), `ruff` (lint), `loguru` (logging), multi-stage `dockerfile` |
| **Docker-First** | `docker-compose.yml` with healthchecks, dependency ordering, named networks/volumes |
| **Migration Ready** | Tortoise ORM built-in migration system (not Alembic) |
| **Environment Config** | Pydantic `BaseSettings` + `.env` with `@lru_cache` |

### 1.2 Areas for Expansion

To evolve from a **minimal starter** into a **standard production template**, the following layers must be introduced:

| Gap | Impact | Mitigation in This Plan |
|-----|--------|------------------------|
| No test infrastructure | Cannot verify correctness at scale | Full test hierarchy with pytest-asyncio, factories, coverage |
| No DI container | Service wiring is manual; hard to mock | `src/dependency/` module with injectable providers |
| No middleware layer | Missing request tracing, timing, logging | `src/middleware/` with request ID, timing, logging middleware |
| No caching layer | Repeated DB hits for hot data | Redis cache abstraction in `src/infrastructure/` |
| No background tasks | Long-running ops block HTTP | `src/task/` + Celery/ARQ structure |
| No auth layer | Most APIs need authentication | `src/auth/` with JWT/OAuth2 skeleton |
| Repo co-located with base | Violates separation | Dedicated `src/data/repo/` directory |
| No API versioning | Breaking changes are hard to manage | `/api/v1/` prefixing strategy |
| No observability | Cannot diagnose production issues | OpenTelemetry + Prometheus metrics scaffolding |
| No CI/CD templates | Manual deployment only | `.github/workflows/` templates |
| No explicit interfaces | Hard to swap implementations | Protocol classes in `src/core/protocol.py` |

### 1.3 Migration Status (As-Built vs. Target)

The plan tracks the evolution from a **minimal starter** to a **standard production template**. The matrix below distinguishes **As-Built** (already implemented in the current codebase) from **Target** (still aspirational):

| Component | Status | Notes |
|-----------|:------:|-------|
| `src/health/` self-contained module | ✅ As-Built | `model/`, `repo/`, `schema/`, `service/`, `route/` all co-located under `src/health/` |
| `src/user/` self-contained module | ✅ As-Built | Mirror of the health module — demonstrates auth + user management |
| `src/route/` thin aggregator | ✅ As-Built | `src/route/__init__.py` aggregates module routers under `/api/v1` |
| `src/service/` shared slot | ✅ As-Built | Placeholder for cross-cutting services (email, notifications) |
| `src/data/db/` Tortoise config + migrations | ✅ As-Built | `0001_initial.py`, `0002_add_health_check_log.py`, `0003_add_user.py` |
| `src/core/` base abstractions | ✅ As-Built | `Base`, `BaseRepo[M]`, `BaseSchema`, `BaseService`, `Success[T]`, `Error`, `protocol.py`, `security.py`, `schema.py` |
| `src/dependency/` centralized DI container | ✅ As-Built | `container.py`, `database.py`, `cache.py`, `auth.py`, `common.py` |
| `src/auth/` JWT/OAuth2/RBAC | ✅ As-Built | `jwt.py`, `oauth2.py`, `permission.py` — full JWT issuance + RBAC |
| `src/middleware/` request-id / timing / logging / error-boundary | ✅ As-Built | `request_id.py`, `timing.py`, `logging.py`, `error_boundary.py` |
| `src/infrastructure/` cache / event-bus / storage | ✅ As-Built | Redis + in-memory cache, memory event bus, local + S3 storage |
| `src/task/` ARQ workers | ✅ As-Built | ARQ worker + `send_email` example job (see ADR-006) |
| Tests | ✅ As-Built | Full test hierarchy with async fixtures, factories, coverage |
| `docs/` architecture / api / deployment / contributing | ✅ As-Built | `architecture.md`, `api.md`, `deployment.md`, `contributing.md` |
| `.github/workflows/` CI/CD | ✅ As-Built | `ci.yml` (lint + typecheck + test) + `cd.yml` (build + push + deploy) |
| Observability (Prometheus metrics) | ✅ As-Built | Hand-rolled Prometheus counters + histogram at `/metrics` |
| API versioning (`/api/v1/`) | ✅ As-Built | Routed via `src/route/__init__.py` prefix |

> **Heads-up — `health` lives under the module folder.** The health endpoint is mounted at `src/health/route/health.py` (`GET /health/check`), not at `src/route/health.py`. All current and future modules follow the same vertical layout.

---

## 2. Architectural Principles

1. **Explicit over Implicit** — Every layer is visible and traceable. No magic imports.
2. **Interface-Driven Design** — Services depend on protocols, not concrete implementations.
3. **Dependency Injection** — All cross-layer dependencies are injected, never hard-coded.
4. **Fail Fast, Fail Loud** — Global error handlers catch everything; custom errors carry context.
5. **Testability by Design** — Every layer is independently unit-testable with mocked dependencies.
6. **Async-First** — All I/O-bound operations are async. No blocking calls in the hot path.
7. **Docker-Native** — Development, testing, and production all run in containers.

---

## 2.5 Module-Centric Architecture

Instead of organizing code by **technical layer** (all routes together, all services together), this template organizes by **domain module** (each module owns all its layers).

### Why Module-Centric?

| Horizontal (Layered) | Module-Centric (Vertical) |
|----------------------|----------------------------|
| `src/route/health.py` + `src/service/health.py` + `src/data/schema/health.py` | `src/health/route/health.py` + `src/health/service/health_service.py` + `src/health/schema/response.py` |
| Scattered across directories | Co-located in one module |
| Hard to delete or extract a feature | Easy to delete or extract a feature |
| Merge conflicts across layers | Merge conflicts isolated to module |
| Unclear ownership | Single module = single owner |
| Cannot extract to microservice later | Can extract `src/item/` → standalone service |

### Module Anatomy

Every domain module follows the same structure:

```
src/<module>/
├── __init__.py              # Module exports (router, public types)
├── model/                   # Tortoise models (subclass core.base.Base)
├── repo/                    # Repositories (subclass BaseRepo[M])
├── schema/                  # Pydantic DTOs (subclass BaseSchema)
│   ├── request.py           # Inbound DTOs (query params, body)
│   └── response.py          # Outbound DTOs (API responses)
├── service/                 # Business logic (subclass BaseService)
│   └── __init__.py          # DI factory: get_<module>_service()
└── route/                   # HTTP endpoints (APIRouter)
    └── __init__.py          # prefix="/<module>", tags=["Module"]
```

### Shared vs. Module-Local

| Shared (`src/core/`, `src/data/`, `src/middleware/`) | Module-Local (`src/<module>/`) |
|------------------------------------------------------|--------------------------------|
| `Base`, `BaseRepo`, `BaseSchema`, `BaseService` | Model, Repo, Schema, Service for that domain |
| `DB_CONFIG`, `init_db`, `run_migration` | DI factory (`get_item_service()`) |
| Global error handlers, middleware | Route definitions |
| Auth infrastructure (JWT, OAuth2) | Module-specific business logic |

**Rule:** Modules may import from shared layers, but shared layers must NEVER import from modules. Modules should not import from each other (use events or shared interfaces for cross-module communication).

---

## 3. Target Project Structure

```
fastapi-template/
│
├── .github/
│   └── workflows/
│       ├── ci.yml                  # Lint, test, coverage on PR
│       └── cd.yml                  # Build, push, deploy on main
│
├── docker/
│   ├── Dockerfile                  # Production multi-stage build
│   ├── Dockerfile.local            # Development build (bind-mount friendly)
│   └── entrypoint.sh             # Container startup script (migrate + serve)
│
├── scripts/
│   ├── migrate.py                  # Standalone migration runner
│   ├── seed.py                     # Database seeding script
│   └── lint.py                     # Unified lint + format + type-check runner
│
├── docs/
│   ├── architecture.md             # ADRs and high-level design decisions
│   ├── api.md                      # OpenAPI/Swagger documentation guide
│   ├── deployment.md               # Production deployment checklist
│   └── contributing.md             # Developer onboarding guide
│
├── src/
│   ├── __init__.py
│   │
│   ├── main.py                     # Application factory: create_app()
│   │
│   ├── config/
│   │   ├── __init__.py             # Re-exports: get_settings, Settings
│   │   ├── config.py               # Pydantic BaseSettings + .env
│   │   └── logging.py              # Loguru configuration, log format, levels
│   │
│   ├── core/                        # SHARED building blocks (read-only for modules)
│   │   ├── __init__.py
│   │   ├── base.py                 # BaseModel (Tortoise), LinkBase, BaseRepo[M], BaseSchema, BaseService
│   │   ├── protocol.py             # Abstract protocols (Repository, Cache, EventBus)
│   │   ├── error.py                # Error, ErrorResponse, Violation, ErrorDetail
│   │   ├── success.py              # Success[T], Meta
│   │   ├── type.py                 # Status, ErrorType, Code enums
│   │   ├── constant.py             # Exception-to-Code/ErrorType mappings
│   │   ├── format.py               # utc_iso_timestamp, formatters
│   │   ├── common.py               # serialize, get_app_version, helpers
│   │   ├── mixin.py                # BaseMixin (tag property)
│   │   └── security.py             # Password hashing, token helpers
│   │
│   ├── data/                        # SHARED data infrastructure (read-only for modules)
│   │   ├── __init__.py
│   │   ├── db/
│   │   │   ├── __init__.py         # DB_CONFIG, init_db, register_tortoise
│   │   │   ├── connection.py       # Connection management, health probes
│   │   │   ├── migration/            # Tortoise migrations (global, versioned)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── 0001_initial.py
│   │   │   │   └── 0002_add_xxx.py
│   │   │   └── model/
│   │   │       ├── __init__.py     # Re-exports all models from all modules
│   │   │       └── user.py         # (optional) Shared / cross-domain models
│   │   │
│   │   └── type/
│   │       ├── __init__.py         # Re-exports: Env, SortOrder
│   │       └── core.py             # Env, SortOrder, Language enums
│   │
│   ├── dependency/                  # SHARED DI container (modules consume, don't define)
│   │   ├── __init__.py
│   │   ├── container.py              # Singleton and factory registrations
│   │   ├── database.py             # DB session / connection dependency
│   │   ├── cache.py                # Redis cache dependency
│   │   ├── auth.py                 # CurrentUser dependency, JWT verification
│   │   └── common.py               # Pagination, sorting dependency factories
│   │
│   ├── auth/                        # SHARED auth infrastructure
│   │   ├── __init__.py
│   │   ├── jwt.py                  # JWT encode/decode, token refresh
│   │   ├── oauth2.py               # OAuth2 password flow scheme
│   │   └── permission.py           # Role-based permission checks
│   │
│   ├── route/                       # ROOT router aggregator (imports from all modules)
│   │   ├── __init__.py             # Root APIRouter, aggregates module routers
│   │   └── api.py                  # Route registration, API metadata, version wiring
│   │
│   ├── service/                     # SHARED / cross-cutting services only
│   │   └── __init__.py             # e.g. email sender, notification dispatcher
│   │
│   ├── middleware/                    # SHARED middleware (cross-cutting concerns)
│   │   ├── __init__.py
│   │   ├── request_id.py           # Inject X-Request-ID, propagate in context
│   │   ├── timing.py               # Log request duration
│   │   ├── logging.py              # Structured access logging
│   │   └── error_boundary.py       # Catch unhandled errors before global handler
│   │
│   ├── task/                        # SHARED background task infrastructure
│   │   ├── __init__.py
│   │   ├── worker.py               # Celery/ARQ worker setup
│   │   └── jobs/
│   │       ├── __init__.py
│   │       └── send_email.py       # Example background job
│   │
│   ├── infrastructure/              # SHARED infrastructure adapters
│   │   ├── __init__.py
│   │   ├── cache/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Cache protocol
│   │   │   ├── redis_cache.py      # Redis implementation
│   │   │   └── memory_cache.py     # In-memory implementation (dev)
│   │   ├── event_bus/
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # EventBus protocol
│   │   │   └── memory_bus.py       # In-memory pub/sub (dev)
│   │   └── storage/
│   │       ├── __init__.py
│   │       ├── base.py             # FileStorage protocol
│   │       ├── local_storage.py    # Local filesystem
│   │       └── s3_storage.py       # AWS S3 / MinIO
│   │
│   ├── util/                        # SHARED utilities
│   │   ├── __init__.py
│   │   ├── pagination.py           # Pagination helper, cursor/page token logic
│   │   ├── sorting.py              # Sort string parsing, validation
│   │   └── validation.py           # Custom Pydantic validators
│   │
│   └── health/                      # EXAMPLE: self-contained domain module
│       ├── __init__.py             # Module exports: health_router
│       ├── model/                  # Domain models (subclass core.base.Base)
│       │   ├── __init__.py
│       │   └── health_check_log.py
│       ├── repo/                   # Data access (subclass BaseRepo[M])
│       │   ├── __init__.py
│       │   └── health_check_log_repo.py
│       ├── schema/                 # Request / response DTOs (subclass BaseSchema)
│       │   ├── __init__.py
│       │   ├── request.py          # HealthLogListParams
│       │   └── response.py         # HealthSchema, DatabaseSchema, HealthCheckLogSchema
│       ├── service/                # Business logic (subclass BaseService)
│       │   ├── __init__.py         # get_health_service() DI factory
│       │   └── health_service.py
│       └── route/                  # HTTP endpoints (APIRouter)
│           ├── __init__.py         # prefix="/health", tags=["Health"]
│           └── health.py             # GET /check
│
├── .env.example
├── .env
├── .env.test
├── .env.production
├── .python-version
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml
├── uv.lock
├── docker-compose.yml
├── makefile
├── README.md
└── plan.md                         # THIS FILE
```

---

## 4. Layer-by-Layer Design

### 4.1 Configuration Layer (`src/config/`)

**Current:** `Settings` via Pydantic `BaseSettings`, `.env` file, `@lru_cache`.

**Target:** Same pattern, expanded with:
- `logging.py` — Loguru configuration (JSON format in production, colored in dev).
- Environment-specific overrides: `.env.test`, `.env.production`.
- Secrets management scaffold (e.g., `SecretStr` for all sensitive fields).

```python
# src/config/config.py
class Settings(BaseSettings):
    # ... existing fields ...
    
    # Cache
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Auth
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Observability
    otel_exporter_endpoint: str | None = None
    prometheus_enabled: bool = False
```

### 4.2 Core Layer (`src/core/`)

**Current:** Excellent base abstractions (`Base`, `BaseRepo`, `BaseSchema`, `BaseService`), `Success[T]`, `Error`, typed enums.

**Target:**
- **Adopt verbatim:** `base.py`, `error.py`, `success.py`, `type.py`, `constant.py`, `format.py`, `common.py`, `mixin.py`.
- **Add:**
  - `protocol.py` — Abstract base classes / protocols for `Repository`, `Cache`, `EventBus`, `FileStorage`.
  - `security.py` — Password hashing (`bcrypt` or `argon2`), JWT helper functions.
  - `schema.py` — Split from `base.py`: `BaseSchema` stays, but add `BaseRequest` and `BaseResponse` for explicit DTO separation.

```python
# src/core/protocol.py
from typing import Protocol, TypeVar

M = TypeVar("M", bound="BaseModel")

class Repository(Protocol[M]):
    async def get_by_id(self, id: UUID) -> M | None: ...
    async def get_many(self, **filters) -> list[M]: ...
    async def create(self, **kwargs) -> M: ...
    async def update(self, id: UUID, **kwargs) -> M | None: ...
    async def delete(self, id: UUID) -> bool: ...
```

### 4.3 Data Layer (`src/data/`)

**Current:** `db/` (Tortoise config, migrations, model registry), `type/` (Env enum).

**Target:**
- **Adopt:** `db/__init__.py`, `db/migration/`, `db/model/` structure.
- **Add:**
  - `db/connection.py` — Dedicated connection pool management, health probes, retry logic.
  - `db/model/__init__.py` — Imports and re-exports models from all domain modules so Tortoise discovers them.

**Module-Local Data Components:**

Each domain module (e.g. `health/`, `user/`) owns its own `model/`, `repo/`, and `schema/` directories. The shared `src/data/` layer only provides infrastructure (DB config, migrations, type enums). Models are registered in `DB_CONFIG` by listing the module's model package (e.g. `"src.health.model"`).

```python
# src/data/db/__init__.py
DB_CONFIG = {
    ...
    "apps": {
        "model": {
            "models": ["src.data.db.model", "src.health.model", "src.user.model"],
            ...
        },
    },
}
```

**Repository Pattern (module-local):**

```python
# src/health/repo/health_check_log_repo.py
from src.core.base import BaseRepo
from src.health.model.health_check_log import HealthCheckLog

class HealthCheckLogRepo(BaseRepo[HealthCheckLog]):
    def __init__(self) -> None:
        super().__init__(HealthCheckLog)
    
    async def get_recent(self, limit: int = 10) -> list[HealthCheckLog]:
        return await self.get_many(order_by="-created_at", limit=limit)
```

**Schema Pattern (module-local):**

```python
# src/health/schema/response.py
from src.core.base import BaseSchema
from src.core.type import Status
from pydantic import Field
from typing import Annotated

class DatabaseSchema(BaseSchema):
    status: Annotated[Status, Field(default=Status.ERROR)]
    version: Annotated[str | None, Field(default=None)]

class HealthSchema(BaseSchema):
    version: Annotated[str, Field(default="0.0.1")]
    db: Annotated[DatabaseSchema | None, Field(default=None)]
```

### 4.4 Dependency Injection Layer (`src/dependency/`)

**Current:** Simple factory functions (`get_health_service()`).

**Target:** Structured DI layer with:
- `container.py` — Singleton and factory registrations.
- `database.py` — `get_db()` dependency for FastAPI `Depends()`.
- `cache.py` — `get_cache()` returning `RedisCache` or `MemoryCache`.
- `auth.py` — `get_current_user()` OAuth2 dependency.
- `common.py` — Pagination (`PaginationParams`), sorting dependencies.

```python
# src/deps/container.py
from functools import lru_cache
from src.data.repo.user_repo import UserRepo
from src.service.user.user_service import UserService
from src.infra.cache.redis_cache import RedisCache


@lru_cache
def get_user_repo() -> UserRepo:
    return UserRepo()


@lru_cache
def get_user_service() -> UserService:
    return UserService(repo=get_user_repo(), cache=get_cache())


@lru_cache
def get_cache() -> RedisCache:
    from src.config import get_settings
    settings = get_settings()
    return RedisCache(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
    )
```

### 4.5 Authentication Layer (`src/auth/`)

**New layer.** Provides:
- `jwt.py` — Token creation, verification, refresh logic.
- `oauth2.py` — FastAPI `OAuth2PasswordBearer` scheme setup.
- `permission.py` — Decorators / dependencies for role-based access control (RBAC).

### 4.6 Route Layer

**As-Built:** `src/route/__init__.py` is a **thin router aggregator** that imports routers from each domain module. The health endpoint lives under the module folder at `src/health/route/health.py` (mounted via `src/health/route/__init__.py` with `prefix="/health"`, `tags=["Health"]`). The flat `src/route/health/` layout from earlier prototypes has been retired.

**Pattern:** Every domain module owns its own routes under `src/<module>/route/`. Each module's `route/__init__.py` exports a router with `prefix="/<module>"` and `tags=["<Module>"]`; the top-level `src/route/__init__.py` only aggregates those module routers. All routes are async and return `JSONResponse` via `Success[T].to_resp()`.

```python
# src/route/__init__.py
from fastapi import APIRouter

from src.health.route import router as _health_router

_subrouters = [_health_router]

router = APIRouter()

for subrouter in _subrouters:
    router.include_router(subrouter)
```

```python
# src/health/route/__init__.py
from fastapi import APIRouter
from .health import router as _health_router

_subrouters = [_health_router]

router = APIRouter(prefix="/health", tags=["Health"])

for subrouter in _subrouters:
    router.include_router(subrouter)
```

```python
# src/health/route/health.py
from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.core.success import Success
from src.health.schema.response import HealthSchema
from src.health.service.health_service import HealthService
from src.health.service import get_health_service

router = APIRouter()

@router.get(path="/check", response_model=Success[HealthSchema])
async def check(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> JSONResponse:
    data = await health_service.check_health()
    return Success.ok(data=data).to_resp()
```

### 4.7 Service Layer (module-local)

**As-Built:** Each domain module owns its own service under `src/<module>/service/`. `HealthService` lives at `src/health/service/health_service.py` with its DI factory `get_health_service()` co-located at `src/health/service/__init__.py`. The shared `src/service/` directory is reserved for **cross-cutting** services (e.g., email, notifications) only — currently a placeholder.

**Target:** No structural change. When new cross-cutting services (email, notification dispatch, etc.) are introduced, they go into `src/service/`; domain services keep going into `src/<module>/service/`.

Each service:
- Subclasses `BaseService`.
- Accepts injected repositories via `__init__`.
- Contains pure business logic (no HTTP, no DB direct access).
- Returns domain objects or schemas, never raw models.

```python
# src/health/service/health_service.py
from src.core.base import BaseService
from src.core.common import get_app_version
from src.core.type import Status
from src.data.db import get_db_health, get_db_version
from src.health.repo.health_check_log_repo import HealthCheckLogRepo
from src.health.schema.response import DatabaseSchema, HealthSchema

class HealthService(BaseService):
    def __init__(self, repo: HealthCheckLogRepo) -> None:
        self._repo = repo

    async def check_health(self) -> HealthSchema:
        db_status = Status.SUCCESS if await get_db_health() else Status.ERROR
        db_version = await get_db_version()

        # Persist for audit trail
        await self._repo.create(status=db_status.value, db_version=db_version)

        return HealthSchema(
            version=get_app_version(),
            db=DatabaseSchema(status=db_status, version=db_version),
        )
```

```python
# src/health/service/__init__.py
from src.health.repo.health_check_log_repo import HealthCheckLogRepo
from src.health.service.health_service import HealthService

def get_health_service() -> HealthService:
    return HealthService(repo=HealthCheckLogRepo())
```

### 4.8 Middleware Layer (`src/middleware/`)

**New layer.** FastAPI middleware for cross-cutting concerns:

| Middleware | Purpose |
|------------|---------|
| `request_id.py` | Inject `X-Request-ID` (UUID4) per request; propagate to logs and downstream calls. |
| `timing.py` | Record request duration; attach to response headers (`X-Response-Time`). |
| `logging.py` | Structured access log (method, path, status, duration, request_id, client_ip). |
| `error_boundary.py` | Last-resort catch before global handler; ensures graceful degradation. |

### 4.9 Task Layer (`src/task/`)

**New layer.** Background job processing scaffold:
- `worker.py` — Celery or ARQ worker configuration.
- `jobs/` — Individual job definitions (e.g., `send_email.py`).
- Jobs are triggered from services, never directly from routes.

### 4.10 Infrastructure Layer (`src/infrastructure/`)

**New layer.** Concrete implementations of core protocols:

| Module | Protocol | Implementation |
|--------|----------|----------------|
| `cache/redis_cache.py` | `Cache` | Redis with `redis-py` or `valkey` |
| `cache/memory_cache.py` | `Cache` | In-memory dict (dev/testing) |
| `event_bus/memory_bus.py` | `EventBus` | In-memory pub/sub (dev) |
| `storage/local_storage.py` | `FileStorage` | Local filesystem |
| `storage/s3_storage.py` | `FileStorage` | AWS S3 / MinIO |

### 4.11 Utility Layer (`src/util/`)

**New layer.** Domain-agnostic helpers:
- `pagination.py` — Cursor-based and offset-based pagination logic.
- `sorting.py` — Parse `?sort=-created_at,name` query strings into Tortoise `order_by`.
- `validation.py` — Custom Pydantic validators (e.g., strong password, phone number).

---

---

## 6. Deployment & Operations

### 6.1 Docker Compose

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Local development: postgres + redis + app |

### 6.2 CI/CD Pipeline (`.github/workflows/`)

**`ci.yml`:**
1. Checkout
2. `uv sync` + cache
3. `ruff check` + `ruff format --check`
4. `mypy` / `ty` type check
5. Upload coverage report

**`cd.yml`:**
1. Build production image
2. Push to registry (GHCR / ECR / Docker Hub)
3. Deploy to staging
4. Deploy to production (blue/green or rolling)

### 6.3 Observability

| Signal | Tool | Implementation |
|--------|------|---------------|
| Metrics | Prometheus | `prometheus-fastapi-instrumentator` or manual counters |
| Traces | OpenTelemetry | `opentelemetry-instrumentation-fastapi` |
| Logs | Loguru + JSON | Structured logging with `request_id` correlation |
| Health | Custom `/health/check` | DB, cache, external API probes |

---

## 7. Development Workflow

### 7.1 Makefile Targets

```makefile
.PHONY: install check test migrate run up down logs seed

install:          # uv sync — install dependencies
	uv sync

check:            # ruff check + ruff format + type check
	uv run ruff check --fix
	uv run ruff format
	uv run ty

test:             # Run full test suite with coverage
	uv run pytest -vv --cov=src --cov-report=term-missing

migrate:          # Run Tortoise migrations
	uv run python -m scripts.migrate

seed:             # Seed database with test data
	uv run python -m scripts.seed

run:              # Local development server with reload
	uv run uvicorn src.main:app --reload --loop uvloop

up:               # docker-compose up -d
	down:             # docker-compose down
	logs:             # docker-compose logs -f
```

### 7.2 Adding a New Module (e.g., `item`)

Follow the **self-contained module** pattern. Create `src/item/` and all its sub-directories, then wire into the shared infrastructure.

```
src/item/
├── __init__.py
├── model/
│   ├── __init__.py
│   └── item.py                 # subclass core.base.Base
├── repo/
│   ├── __init__.py
│   └── item_repo.py            # subclass BaseRepo[Item]
├── schema/
│   ├── __init__.py
│   ├── request.py              # ItemCreateRequest, ItemUpdateRequest
│   └── response.py             # ItemResponse, ItemListResponse
├── service/
│   ├── __init__.py             # get_item_service() DI factory
│   └── item_service.py         # subclass BaseService
└── route/
    ├── __init__.py             # APIRouter(prefix="/items", tags=["Items"])
    └── item.py                 # CRUD endpoints
```

**Wiring checklist:**

1. **Register model** in `src/data/db/__init__.py`:
   ```python
   "models": [..., "src.item.model"],
   ```

2. **Re-export model** in `src/data/db/model/__init__.py`:
   ```python
   from src.item.model import Item
   ```

3. **Create migration** in `src/data/db/migration/` (e.g., `0003_add_item.py`).

4. **Register route** in `src/route/__init__.py`:
   ```python
   from src.item.route import router as _item_router
   _subrouters = [..., _item_router]
   ```



---

## 8. Risk Analysis & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tortoise ORM migration limitations | Medium | High | Document Tortoise-specific migration patterns; provide CLI helper scripts |
| Async code blocking event loop | Medium | High | Code review checklist; `uvloop` in production; monitoring for loop lag |
| Secret leakage in logs | Low | Critical | `SecretStr` everywhere; log redaction middleware; pre-commit secret scan |
| Test flakiness (async DB) | Medium | Medium | Testcontainers for isolated DB; transaction rollback per test |
| Cache inconsistency | Medium | High | Cache invalidation strategy in service layer; TTL defaults; cache warming |
| JWT token expiration edge cases | Low | Medium | Refresh token rotation; sliding window; explicit expiry |

---

## 9. Decision Log (ADR)

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Keep Tortoise ORM (not SQLAlchemy) | Existing expertise; built-in async; migration system already in place | Adopted |
| ADR-002 | Use `uv` not `poetry`/`pip` | Speed; lockfile; modern PEP 621 support | Adopted |
| ADR-003 | Response envelope (`Success[T]`, `Error`) | Consistent API contract; easier client consumption | Adopted |
| ADR-004 | No SQLAlchemy + Alembic | Avoid dual ORM complexity; Tortoise migrations suffice | Adopted |
| ADR-005 | Protocol-based DI (not `dependency-injector` lib) | Avoid heavy framework; standard Python `typing.Protocol` | Proposed |
| ADR-006 | ARQ for tasks (not Celery / RQ) | Pure async (no sync layer); Redis already a dependency; minimal boilerplate vs Celery. Celery kept as upgrade path if Beat / multi-broker needed. | Adopted |
| ADR-007 | Redis for cache + message broker | Single infrastructure component; widely supported | Proposed |
| ADR-008 | OpenTelemetry for observability | Vendor-neutral; supports multiple backends | Proposed |
| ADR-009 | Versioned API (`/api/v1`) | Enables backward-compatible evolution | Proposed |
| ADR-010 | Pydantic v2 throughout | FastAPI native; performance; strict typing | Adopted |
| **ADR-011** | **Module-Centric Architecture** | Each domain module is self-contained (model, repo, schema, service, route). Shared infrastructure lives in `src/core/`, `src/data/`, `src/middleware/`. Modules import from shared layers but not from each other. This enables parallel development, clear ownership, and easy extraction into microservices. | **Adopted** |

---

## 10. Summary

This plan has been fully implemented, transforming the initial **minimal FastAPI starter** into a **standard production template**:

1. **Adopted** all proven patterns from the original codebase (4-tier architecture, base abstractions, response envelopes, error handling, modern tooling).
2. **Implemented** a **module-centric architecture** with two fully self-contained domain modules (`health/` and `user/`), each owning its own model, repo, schema, service, and route layers. Shared infrastructure (core, data, middleware, auth) is read-only for modules.
3. **Added** all production layers: testing (unit/integration/e2e), DI container, middleware (error boundary, logging, timing, request ID), auth (JWT/OAuth2/RBAC), caching (Redis + in-memory), background tasks (ARQ), infrastructure abstractions (cache, event bus, file storage), observability (Prometheus metrics), and CI/CD pipelines.
4. **Structured** the codebase for scalability: explicit request/response DTOs, protocol-driven interfaces, and comprehensive documentation.
5. **Maintained** the core philosophy: **explicit, async, testable, docker-native**.

The result is a template that teams can clone, configure via `.env`, and deploy within minutes — while having a clear growth path from a single self-contained module to a complex, multi-domain service.
