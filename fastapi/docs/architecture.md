# Architecture

> **Status:** Living document — updated alongside the codebase.
> **Last Updated:** 2026-07-01

## Architecture Overview

Four-tier, module-centric architecture on top of FastAPI:

```
Request
  └── Middleware stack (error_boundary → logging → timing → request_id → cors → prometheus)
        └── Router aggregator (/api/v1/*)
              └── Module router (e.g. /health, /users/auth)
                    └── Route handler (thin — validates, delegates, responds)
                          └── Service (business logic, orchestrates repos)
                                └── Repository (data access via Tortoise ORM)
                                      └── Model (Tortoise ORM model, maps to PostgreSQL)
```

### Module-Centric (Vertical Slicing)

Each domain is self-contained under `src/<module>/`:

```
src/<module>/
  ├── __init__.py          # Module exports (router, public types)
  ├── model/               # Tortoise ORM models
  ├── repo/                # Data access (subclass BaseRepo[M])
  ├── schema/              # Pydantic DTOs (request.py / response.py)
  ├── service/             # Business logic (subclass BaseService)
  └── route/               # FastAPI APIRouter
```

### Shared Layers

| Layer | Path | Purpose |
|-------|------|---------|
| Core | `src/core/` | Base classes, protocols, enums, error/success envelopes, security |
| Config | `src/config/` | Pydantic settings, logging config |
| Data | `src/data/` | DB config, connection management, migrations, model registry |
| Dependency | `src/dependency/` | DI container, auth/cache/common dependencies |
| Auth | `src/auth/` | JWT issuance, OAuth2 scheme, RBAC |
| Middleware | `src/middleware/` | Error boundary, logging, timing, request ID |
| Infrastructure | `src/infrastructure/` | Cache (Redis/memory), event bus, file storage |
| Task | `src/task/` | ARQ background worker + jobs |
| Observability | `src/observability/` | Prometheus metrics |
| Route | `src/route/` | Root router aggregator (prefix `/api/v1`) |
| Service | `src/service/` | Cross-cutting services (email, notifications) |
| Util | `src/util/` | Pagination, sorting, validation helpers |

**Rule:** Modules may import from shared layers. Shared layers must NEVER import from modules. Modules should not import from each other.

---

## ADR Log

### ADR-001: Tortoise ORM (not SQLAlchemy)
**Status:** Adopted  
**Rationale:** Existing expertise; built-in async; migration system already in place. Tortoise's migration system is simpler than Alembic for this template's needs.

### ADR-002: `uv` (not poetry/pip)
**Status:** Adopted  
**Rationale:** Speed; single-binary install; PEP 621 support; lockfile.

### ADR-003: Response Envelope (`Success[T]`, `Error`)
**Status:** Adopted  
**Rationale:** Consistent API contract — every response has a predictable shape `{status, code, message, data, meta, timestamp}`. Easier client consumption.

### ADR-004: No SQLAlchemy + Alembic
**Status:** Adopted  
**Rationale:** Avoid dual ORM complexity. Tortoise migrations suffice.

### ADR-005: Protocol-based DI (not `dependency-injector` lib)
**Status:** Adopted  
**Rationale:** Avoid heavy framework; standard Python `typing.Protocol`; structural typing enables easy mocking.

### ADR-006: ARQ for Background Tasks (not Celery)
**Status:** Adopted  
**Rationale:** Pure async (no sync compatibility layer); Redis already a dependency; minimal boilerplate. Celery would add Celery Beat and multi-broker support if needed later.

### ADR-007: Redis for Cache + Message Broker
**Status:** Adopted  
**Rationale:** Single infrastructure component; widely supported; serves both cache and ARQ backend.

### ADR-008: Prometheus for Metrics (hand-rolled, not instrumentator lib)
**Status:** Adopted  
**Rationale:** Full control over label cardinality; one fewer dependency; only expose what we use.

### ADR-009: Versioned API (`/api/v1`)
**Status:** Adopted  
**Rationale:** Enables backward-compatible evolution; routes mounted under `/api/v1` in `src/route/__init__.py`.

### ADR-010: Pydantic v2
**Status:** Adopted  
**Rationale:** FastAPI native; performance improvements; strict typing.

### ADR-011: Module-Centric Architecture
**Status:** Adopted  
**Rationale:** Each domain module is self-contained (model, repo, schema, service, route). Enables parallel development, clear ownership, easy extraction into microservices.

---

## Key Design Decisions

### Why `BaseHTTPMiddleware` and not `@app.middleware("http")`?

`BaseHTTPMiddleware` gives us a `dispatch` method with a `call_next` coroutine, which allows proper exception handling, state management on `request.state`, and post-processing on the response. The decorator form is more limited.

### Why `runtime_checkable` Protocol?

Makes `isinstance(obj, Repository)` work at runtime, which is useful for DI container validation and testing.

### Why in-memory defaults for infrastructure?

The template ships with `MemoryCache`, `MemoryEventBus`, and `LocalFileStorage` so the app runs without external dependencies during development. Swap for Redis/S3 via the DI container when deploying.

---

## Request Flow (Detail)

```
Client → PrometheusMiddleware (metrics counter + timer)
  → CORSMiddleware (CORS headers, if configured)
    → RequestIdMiddleware (inject/propagate X-Request-ID)
      → TimingMiddleware (record X-Response-Time)
        → LoggingMiddleware (structured access log)
          → ErrorBoundaryMiddleware (catch-all exception handler)
            → FastAPI Router (/api/v1)
              → Module Router
                → Route Handler
                  → Service
                    → Repository
                      → Tortoise ORM → PostgreSQL
```

Starlette applies middleware in reverse registration order: **last registered runs first (outermost)**. The registration order in `create_app()` produces the chain above.
