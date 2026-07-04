# FastAPI Template — Complete Project Blueprint

A production-ready FastAPI starter with PostgreSQL, Tortoise ORM, JWT auth, middleware stack, caching, file storage, event bus, background tasks, Prometheus metrics, and CI/CD.

> **Purpose:** This document is the single source of truth for recreating the template in a new project. Every file, configuration, and architectural decision is captured below.

---

## Table of Contents

1. [Stack](#stack)
2. [Project Structure](#project-structure)
3. [Root Configuration Files](#root-configuration-files)
4. [Docker & Orchestration](#docker--orchestration)
5. [CI/CD](#cicd)
6. [Makefile Commands](#makefile-commands)
7. [Architecture](#architecture)
8. [Source Code (`src/`)](#source-code-src)
   - [Application Factory (`src/main.py`)](#application-factory)
   - [Core Layer (`src/core/`)](#core-layer)
   - [Config Layer (`src/config/`)](#config-layer)
   - [Auth Layer (`src/auth/`)](#auth-layer)
   - [Data Layer (`src/data/`)](#data-layer)
   - [Infra Layer (`src/infra/`)](#infra-layer)
   - [Module Layer (`src/module/`)](#module-layer)
   - [Shared Layer (`src/shared/`)](#shared-layer)
   - [Task/Background Jobs (`src/task/`)](#task-layer)
9. [Scripts (`scripts/`)](#scripts)
10. [API Endpoints](#api-endpoints)
11. [Environment Variables](#environment-variables)
12. [Quick Start](#quick-start)
13. [Adding a New Module](#adding-a-new-module)

---

## Stack

| Category | Choice |
|---|---|
| **Language** | Python 3.14.6 (pinned via `.python-version`) |
| **Package manager** | [uv](https://docs.astral.sh/uv/) |
| **Web framework** | FastAPI 0.136.1 (`fastapi[all]`) |
| **ASGI server** | uvicorn (uvloop) |
| **ORM** | Tortoise ORM 1.1.7 (`asyncpg` + `accel`) |
| **Database** | PostgreSQL 18 |
| **Auth** | PyJWT 2.10.1 (HS256), bcrypt 5.0.0, OAuth2 Password Bearer |
| **Cache** | Redis 6.4.0 (async `redis-py`) + in-memory fallback |
| **Event bus** | In-memory pub/sub (pluggable: Redis Streams, Kafka, NATS) |
| **File storage** | Local filesystem + S3 (`aioboto3`, optional) |
| **Background tasks** | ARQ (async Redis-based job queue, optional) |
| **Observability** | Prometheus client 0.21.1 (hand-rolled middleware) |
| **Logging** | Loguru 0.7.3 (text or JSON format) |
| **Linting/formatting** | Ruff 0.15.12 |
| **Type checking** | `ty` 0.0.33 |
| **Pre-commit** | Ruff + trailing-whitespace + check-yaml/toml + detect-secrets |
| **Testing** | pytest (with coverage) |
| **Containerization** | Docker multi-stage build + docker-compose |
| **CI/CD** | GitHub Actions (lint → test → coverage → build/push → deploy) |

---

## Project Structure

```
fastapi/
├── .dockerignore
├── .env
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── .pre-commit-config.yaml
├── .python-version
├── README.md
├── docker-compose.yml
├── dockerfile
├── docs/
│   ├── api.md
│   ├── architecture.md
│   ├── contributing.md
│   ├── deployment.md
│   └── plan.md
├── makefile
├── pyproject.toml
├── ruff.toml
├── scripts/
│   ├── __init__.py
│   ├── lint.py
│   ├── migrate.py
│   └── seed.py
└── src/
    ├── __init__.py
    ├── main.py
    ├── auth/
    │   ├── __init__.py
    │   ├── jwt.py
    │   ├── oauth2.py
    │   └── permission.py
    ├── config/
    │   ├── __init__.py
    │   ├── config.py
    │   └── logging.py
    ├── core/
    │   ├── __init__.py
    │   ├── base.py
    │   ├── common.py
    │   ├── constant.py
    │   ├── error.py
    │   ├── format.py
    │   ├── mixin.py
    │   ├── protocol.py
    │   ├── schema.py
    │   ├── security.py
    │   ├── success.py
    │   └── type.py
    ├── data/
    │   ├── __init__.py
    │   └── db/
    │       ├── __init__.py
    │       ├── connection.py
    │       ├── migration/
    │       │   ├── __init__.py
    │       │   └── 0001_initial.py
    │       ├── model/
    │       │   ├── __init__.py
    │       │   ├── health_check_log.py
    │       │   └── user.py
    │       └── repo/
    │           ├── __init__.py
    │           ├── health_check_log_repo.py
    │           └── user_repo.py
    ├── infra/
    │   ├── __init__.py
    │   ├── cache/
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   ├── memory_cache.py
    │   │   └── redis_cache.py
    │   ├── event_bus/
    │   │   ├── __init__.py
    │   │   ├── base.py
    │   │   └── memory_bus.py
    │   └── storage/
    │       ├── __init__.py
    │       ├── base.py
    │       ├── local_storage.py
    │       └── s3_storage.py
    ├── module/
    │   ├── __init__.py
    │   ├── health/
    │   │   ├── __init__.py
    │   │   ├── route/
    │   │   │   ├── __init__.py
    │   │   │   └── health.py
    │   │   ├── schema/
    │   │   │   ├── __init__.py
    │   │   │   ├── request.py
    │   │   │   └── response.py
    │   │   └── service/
    │   │       ├── __init__.py
    │   │       └── health_service.py
    │   └── user/
    │       ├── __init__.py
    │       ├── route/
    │       │   ├── __init__.py
    │       │   ├── auth.py
    │       │   └── user.py
    │       ├── schema/
    │       │   ├── __init__.py
    │       │   ├── request.py
    │       │   └── response.py
    │       └── service/
    │           ├── __init__.py
    │           └── user_service.py
    ├── shared/
    │   ├── __init__.py
    │   ├── deps/
    │   │   ├── __init__.py
    │   │   ├── auth.py
    │   │   ├── cache.py
    │   │   ├── common.py
    │   │   └── container.py
    │   ├── middleware/
    │   │   ├── __init__.py
    │   │   ├── error_boundary.py
    │   │   ├── logging.py
    │   │   ├── request_id.py
    │   │   └── timing.py
    │   ├── observability/
    │   │   ├── __init__.py
    │   │   └── metrics.py
    │   └── util/
    │       ├── __init__.py
    │       ├── pagination.py
    │       ├── sorting.py
    │       └── validation.py
    └── task/
        ├── __init__.py
        ├── worker.py
        └── jobs/
            ├── __init__.py
            └── send_email.py
```

---

## Root Configuration Files

### `.python-version`
```
3.14.6
```

### `pyproject.toml`
```toml
[project]
name = "fastapi-template"
version = "0.0.1"
description = "Standard production-ready FastAPI template (Postgres + Tortoise ORM + auth + middleware + cache)."
requires-python = "==3.14.6"
dependencies = [
    ### core ###
    "toml==0.10.2",
    "loguru==0.7.3",
    "fastapi[all]==0.136.1",
    "pydantic-settings==2.7.0",
    ### db ###
    "tortoise-orm[asyncpg,accel]==1.1.7",
    ### auth ###
    "PyJWT[crypto]==2.10.1",
    "bcrypt==5.0.0",
    ### observability ###
    "prometheus-client==0.21.1",
    ### infra (optional — used by infra/cache/redis_cache.py) ###
    "redis==6.4.0",
]

[dependency-groups]
dev = [
    "pre-commit==4.6.0",
    "ruff==0.15.12",
    "ty==0.0.33",
]

[tool.tortoise]
tortoise_orm = "src.data.db.DB_CONFIG"

[tool.coverage.run]
source = ["src"]
omit = ["*/migration/*"]

[tool.coverage.report]
show_missing = true
skip_covered = false
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
]

[tool.ruff]
target-version = "py314"
line-length = 100
extend-exclude = [".venv", ".ruff_cache", "build", "dist"]

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM", "TID", "RUF"]
ignore = ["E501", "B008", "RUF012"]

[tool.ruff.lint.per-file-ignores]
"scripts/**/*.py" = ["T201"]
```

### `ruff.toml`
```toml
target-version = "py314"
line-length = 120
src = ["src"]

[lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM", "RUF"]
ignore = ["E501"]

[lint.per-file-ignores]
"src/deps/**/*.py" = ["B008"]
"src/route/**/*.py" = ["B008"]

[format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

### `.gitignore`
```
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
.eggs/
build/
dist/
.venv/
venv/
ENV/
.ruff_cache/
.pytest_cache/
.coverage
.coverage.*
htmlcov/
coverage.xml
*.cover
.mypy_cache/
.ty_cache/
.env
.env.*.local
!.env.example
!.env.test
!.env.production
.idea/
.vscode/
*.swp
*.swo
.DS_Store
Thumbs.db
*.log
logs/
node_modules/
```

### `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.12
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-toml
      - id: check-added-large-files
        args: [--maxkb=512]
      - id: detect-private-key
      - id: check-merge-conflict
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: [--baseline, .secrets.baseline]
        exclude: |
          (?x)^(
            .*\.example|
            .*/tests/.*|
            .*\.md
          )$
```

### `.dockerignore`
```
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.ruff_cache
.venv
.coverage
htmlcov
.git
.gitignore
.idea
.vscode
*.md
docs/
tests/
.dockerignore
dockerfile
docker-compose*.yml
.env*
!.env.example
```

### `.env.example`
```
# core
ENV=local
DEBUG=true
LOG_FORMAT=text
# db (db = compose service; use localhost when running the app on the host)
DB_SCHEMA=postgresql
DB_HOST=db
DB_PORT=5432
DB_USER=user
DB_PASSWORD=password
DB_NAME=app
# cors: comma-separated origins; leave empty for same-origin only
CORS_ORIGINS=
# auth — generate a real secret with: openssl rand -hex 32
JWT_SECRET=local-dev-secret-change-me
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
# cache
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
CACHE_TTL_DEFAULT=300
# observability
METRICS_ENABLED=true
```

### `.env`
```
# core
ENV=local
DEBUG=true
DB_SCHEMA=postgresql
DB_HOST=db
DB_PORT=5432
DB_USER=user
DB_PASSWORD=password
DB_NAME=app
CORS_ORIGINS=
```

---

## Docker & Orchestration

### `dockerfile` — Multi-stage build
```dockerfile
### base image ###
ARG PYTHON_VERSION=3.14.3
FROM python:$PYTHON_VERSION AS base

ARG ENV
ARG WORK_DIR
ARG INSTALL_DIR
ARG PW_DIR

ENV ENV=$ENV
ENV WORK_DIR=$WORK_DIR
ENV INSTALL_DIR=$INSTALL_DIR
ENV PW_DIR=$PW_DIR
ENV PYTHONUNBUFFERED=true
ENV PYTHONFAULTHANDLER=true
ENV PYTHONDONTWRITEBYTECODE=true
ENV PYTHONHASHSEED=random
ENV VENV_PATH="$INSTALL_DIR/.venv"
ENV PATH="$VENV_PATH/bin:$PATH"

### builder image ###
FROM base AS builder
ARG ENV WORK_DIR INSTALL_DIR PW_DIR
ENV ENV=$ENV WORK_DIR=$WORK_DIR INSTALL_DIR=$INSTALL_DIR PW_DIR=$PW_DIR

RUN pip install --upgrade pip
RUN pip install uv

WORKDIR $INSTALL_DIR
COPY pyproject.toml $INSTALL_DIR
RUN uv venv
RUN uv pip install -r $INSTALL_DIR/pyproject.toml

### local image ###
FROM base AS local
ARG ENV WORK_DIR INSTALL_DIR PW_DIR
ENV ENV=$ENV WORK_DIR=$WORK_DIR INSTALL_DIR=$INSTALL_DIR PW_DIR=$PW_DIR

WORKDIR $WORK_DIR
COPY --from=builder $INSTALL_DIR $INSTALL_DIR
COPY . $WORK_DIR
```

### `docker-compose.yml`
```yaml
services:
  db:
    image: postgres:18
    hostname: db-app
    container_name: db-app
    restart: on-failure
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    ports:
      - "5432:5432"
    networks:
      - db
    volumes:
      - db:/var/lib/postgresql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
      start_period: 10s
      interval: 5s
      timeout: 3s
      retries: 3

  server:
    hostname: server-app
    container_name: server-app
    restart: unless-stopped
    build:
      context: .
      dockerfile: dockerfile
      target: local
      args:
        ENV: local
        WORK_DIR: /workdir
        INSTALL_DIR: /opt/install
        PW_DIR: /pwdir
    ports:
      - "8000:8000"
    volumes:
      - .:/workdir
    networks:
      - db
      - server
    depends_on:
      db:
        condition: service_healthy
    env_file:
      - .env
    command: >
      bash -c "python -m scripts.migrate &&
      uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload --loop uvloop"

networks:
  db:
    name: db-app
    driver: bridge
  server:
    name: server-app
    driver: bridge

volumes:
  db:
    name: db-app
```

---

## CI/CD

### `.github/workflows/ci.yml`
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: "3.14"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          enable-cache: true
      - run: uv sync --group dev
      - run: uv run ruff check
      - run: uv run ruff format --check
      - run: uv run ty check src/

  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:18
        env:
          POSTGRES_USER: user
          POSTGRES_PASSWORD: password
          POSTGRES_DB: app
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          enable-cache: true
      - run: uv sync --group dev
      - run: uv run pytest -vv --cov=src --cov-report=xml --cov-report=term-missing
        env:
          ENV: test
          DB_HOST: localhost
          DB_PORT: 5432
          DB_USER: user
          DB_PASSWORD: password
          DB_NAME: app
          DB_SCHEMA: postgresql
          JWT_SECRET: ci-secret-do-not-use-in-production
          DEBUG: "true"
      - uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: false
```

### `.github/workflows/cd.yml`
```yaml
name: CD

on:
  push:
    branches: [main]
    tags: ["v*"]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix=
      - uses: docker/build-push-action@v6
        with:
          context: .
          file: dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: staging
    steps:
      - run: |
          echo "Deploying ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }} to staging..."
          # Add your staging deployment command

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/v')
    environment: production
    steps:
      - run: |
          echo "Deploying ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.ref_name }} to production..."
          # Add your production deployment command
```

---

## Makefile Commands

```makefile
DOCKER_COMPOSE := docker compose -f docker-compose.yml
UV := uv
UVX := $(UV)x

clean-db:   $(DOCKER_COMPOSE) down -v
clean:      $(DOCKER_COMPOSE) down -v --rmi all
ps:         $(DOCKER_COMPOSE) ps -a
build:      COMPOSE_BAKE=true $(DOCKER_COMPOSE) build
up:         $(DOCKER_COMPOSE) up -d
stop:       $(DOCKER_COMPOSE) stop
down:       $(DOCKER_COMPOSE) down
restart:    make stop && make build && make up
logs:       $(DOCKER_COMPOSE) logs -f
install:    $(UV) sync --all-groups
check:      make install && $(UVX) ruff check --fix && $(UVX) ruff format --check
format:     $(UVX) ruff format
lint:       $(UVX) ruff check
typecheck:  $(UVX) ty check src/
migrate:    $(UV) run python -m scripts.migrate
seed:       $(UV) run python -m scripts.seed
run:        $(UV) run uvicorn src.main:app --reload --loop uvloop
export:     $(UV) export --format requirements-txt --output requirements.txt
```

---

## Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────┐
│                  Route (HTTP)                    │  ← FastAPI routers, Depends()
├─────────────────────────────────────────────────┤
│               Service (Business Logic)           │  ← Pure domain logic
├─────────────────────────────────────────────────┤
│               Repo (Data Access)                 │  ← CRUD, query building
├─────────────────────────────────────────────────┤
│              Model (DB / Domain)                 │  ← Tortoise ORM models
└─────────────────────────────────────────────────┘
```

### Module-Centric (Vertical Slicing)

Each domain feature is its own module under `src/module/<name>/`:

```
module/<name>/
├── __init__.py          → re-exports, DI factory for service
├── route/               → FastAPI router(s)
│   ├── __init__.py      → aggregates sub-routers
│   └── *.py             → individual route files
├── schema/
│   ├── __init__.py      → re-exports
│   ├── request.py       → request DTOs (BaseRequest)
│   └── response.py      → response DTOs (BaseResponse)
└── service/
    ├── __init__.py      → DI factory e.g. get_health_service()
    └── service.py       → service class
```

### Middleware Stack (applied top-to-bottom)

```
LoggingMiddleware (outermost)
  └── TimingMiddleware
        └── RequestIdMiddleware
              └── CORSMiddleware (only if origins configured)
                    └── ErrorBoundaryMiddleware (innermost)
                          └── routes / metrics
```

### Request Flow

```
Client → FastAPI → Middleware[5] → Router(/api/v1) → Module Router
  → Route handler → Depends() injection → Service method
    → Repo method → Tortoise ORM → PostgreSQL
  → Service returns schema → Success[T].to_resp() → JSONResponse
```

### Response Envelope

**Success:**
```json
{
  "status": "success",
  "code": 200,
  "message": null,
  "data": { ... },
  "meta": null,
  "timestamp": "2026-07-01T12:00:00Z"
}
```

**Error:**
```json
{
  "status": "error",
  "code": 404,
  "message": "Resource not found",
  "type": "not_found",
  "details": null,
  "retry_able": false,
  "timestamp": "2026-07-01T12:00:00Z"
}
```

### Key Design Decisions (ADRs)

1. **ORM**: Tortoise ORM (async, native asyncpg, built-in migrations)
2. **Response envelope**: Custom `Success[T]` generic (not plain dicts)
3. **Error handling**: Custom `Error` exception class with factory methods, mapped to JSON
4. **Auth**: JWT (access + refresh tokens), bcrypt passwords, OAuth2PasswordBearer
5. **Protocol-based DI**: `typing.Protocol` for Cache, EventBus, FileStorage (not ABCs)
6. **Module-centric structure**: Vertical slicing per domain, not horizontal layers
7. **In-memory defaults**: Cache, event bus, storage default to in-memory (swap per env)
8. **Logging**: Loguru (not stdlib logging) with structured JSON output
9. **Linting**: Ruff (not Black + isort + flake8 + pyupgrade)
10. **Type checking**: `ty` (not mypy — faster, Python 3.14 compatible)
11. **Observability**: Hand-rolled Prometheus middleware (not instrumentator)

---

## Source Code (`src/`)

### Application Factory

#### `src/main.py`

Wires the entire application:

```python
# Creates FastAPI app via create_app()
# Middleware order (last-added runs innermost):
#   ErrorBoundaryMiddleware → Logging → Timing → RequestId → CORS → Prometheus
# Routes under /api/v1/ prefix
# Init global error handlers, Tortoise ORM, metrics endpoint /metrics

@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    yield
```

### Core Layer

#### `src/core/type.py` — Shared enums

- `Env` (LOCAL, DEV, PROD, TEST)
- `Status` (SUCCESS, ERROR)
- `ErrorType` — comprehensive error type string enum (all HTTP, auth, business logic, DB, file, email categories)
- `Code` — IntEnum of all HTTP status codes (1xx–5xx) using starlette.status

#### `src/core/base.py` — Base model, repo, schema, service

**Base (Tortoise model):**
- Fields: `id` (UUID PK), `created_at`, `updated_at`, `deleted_at` (soft delete)
- Methods: `soft_delete()`, `get_active()`, `db_fields()`, `from_query_result()`

**LinkBase** — for M2M association tables (same fields minus `deleted_at`)

**BaseRepo[M] (generic repo):**
- Methods: `count()`, `first_by_raw()`, `exists()`, `get_or_create()`, `create()`, `get_or_none()`, `get_by_id()`, `get_ids()`, `get_one()`, `get_many()`, `get_paginated()`, `filter_existing_ids()`, `bulk_create()`, `update()`, `delete()`, `delete_by_filter()`
- Logging via `_tag` property

**BaseSchema (Pydantic):**
- `model_config = ConfigDict(from_attributes=True)`
- Methods: `to_json()`, `to_dict()`, `safe_dump()`, `log()`

**BaseService:**
- Constructor logs instantiation
- `_tag` property for class name

#### `src/core/schema.py` — Split DTO bases

- `BaseRequest` (extends BaseSchema, `extra="forbid"`)
- `BaseResponse` (extends BaseSchema)
- `PaginationMeta` with `.build()` class method

#### `src/core/error.py` — Error handling

**Violation, ErrorDetail, ErrorResponse** schemas

**Error class (Exception):**
- Fields: status, code, message, type, details, retry_able, timestamp
- Factory methods: `.bad_request()`, `.unauthorized()`, `.not_found()`, `.forbidden()`, `.conflict()`, `.request_timeout()`, `.process_exception()`, `.process_validation_error()`
- Serialization: `to_dict()`, `to_json()`, `to_resp()` (JSONResponse)

**`init_global_errors(app)`**: Registers exception handlers for `HTTPException`, `RequestValidationError`, `Error`, and generic `Exception` (with traceback logging + GC)

**`error_api_responses()`**: Returns OpenAPI response specs for 400/401/403/404/422/500

#### `src/core/success.py` — Success envelope

**Success[T] (generic):**
- Fields: status (SUCCESS), code, message, data (T), meta, timestamp (auto UTC)
- Factory methods: `.new()`, `.ok()` (200), `.created()` (201), `.no_content()` (204)
- `to_resp()` returns `JSONResponse`

#### `src/core/security.py` — Password hashing + JWT

- `hash_password(plain)` — bcrypt, 12 rounds
- `verify_password(plain, hashed)` — constant-time check
- `encode_token(subject, secret, algorithm, expires_in, token_type)` — JWT encode
- `decode_token(token, secret, algorithm, expected_type)` — decode with validation; raises Error for expired/invalid/wrong-type
- `TokenPayload` — Pydantic model: sub, type, iat, exp, jti

#### `src/core/protocol.py` — Abstract protocols

- `Repository[M]` — generic repository contract
- `Cache` — get/set/delete/exists/clear
- `EventBus` — publish/subscribe
- `FileStorage` — put/get/delete/url

#### `src/core/common.py` — Utility functions

- `get_app_version()` — reads version from pyproject.toml
- `serialize(obj)` — recursive serializer handling BaseModel, dict, list, Enum, datetime, UUID, SecretStr, etc.

#### `src/core/constant.py` — Exception-to-code mapping

Maps Python exceptions (ValueError, KeyError, DoesNotExist, IntegrityError, etc.) to Code and ErrorType.

#### `src/core/format.py`

- `utc_iso_timestamp()` → "2026-07-01T12:00:00Z"

#### `src/core/mixin.py`

- `BaseMixin` — provides `_tag` property (class name)

### Config Layer

#### `src/config/config.py` — Settings via pydantic-settings

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: Env
    debug: bool
    log_format: str = "text"

    # DB
    db_schema: str
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_password: SecretStr

    # CORS
    cors_origins: str = ""  # comma-separated

    # Auth
    jwt_secret: SecretStr
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Cache
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: SecretStr | None = None
    cache_ttl_default: int = 300

    # Observability
    metrics_enabled: bool = True

    @property
    def cors_origin_list(self) -> list[str]: ...
```

`get_settings()` is cached via `@lru_cache`.

#### `src/config/logging.py` — Loguru config

- Debug mode → `DEBUG` level, else `INFO`
- `LOG_FORMAT=json` → JSON structured output; else colored text format
- `configure_logging()` — idempotent, removes existing handlers, adds stdout sink

### Auth Layer

#### `src/auth/jwt.py` — JWT issuance

```python
@dataclass
class IssuedTokenPair:
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class JWTIssuer:
    def issue_access(self, user_id) -> str
    def issue_refresh(self, user_id) -> str
    def issue_pair(self, user_id) -> IssuedTokenPair

jwt_issuer = JWTIssuer()  # singleton
```

#### `src/auth/oauth2.py` — OAuth2 scheme

```python
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)
```

#### `src/auth/permission.py` — RBAC

- `Role` (USER, ADMIN, SUPERADMIN)
- `Permission` (USER_READ, USER_WRITE, USER_DELETE, ADMIN_READ, ADMIN_WRITE)
- `CurrentPrincipal` — user_id + role
- `require_role(*allowed)` — dependency factory (401/403)
- `require_permission(permission)` — dependency factory (401/403)

### Data Layer

#### `src/data/db/__init__.py` — DB config + init

```python
DB_CONFIG = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": settings.db_host,
                "port": settings.db_port,
                "user": settings.db_user,
                "password": serialize(settings.db_password),
                "database": settings.db_name,
            },
        }
    },
    "apps": {
        "model": {
            "models": ["src.data.db.model"],
            "default_connection": "default",
            "migrations": "src.data.db.migration",
        },
    },
}
```

- `get_db_health()` → bool
- `get_db_version()` → PostgreSQL version string
- `init_db(app)` → registers Tortoise with FastAPI
- `run_migration()` → applies pending Tortoise migrations

#### `src/data/db/connection.py` — Connection management

- `wait_for_db(max_retries=10)` — exponential backoff with jitter
- `get_pool_stats()` — pool metrics dict
- `close_all()` — graceful shutdown

#### `src/data/db/model/user.py`

```python
class User(Base):
    email: str (unique, indexed)
    username: str (unique, indexed)
    hashed_password: str
    full_name: str | None
    role: str (default "user")
    is_active: bool (default True)
    last_login_at: datetime | None
    table = "user"
```

#### `src/data/db/model/health_check_log.py`

```python
class HealthCheckLog(Base):
    status: str
    response_time_ms: float | None
    db_version: str | None
    table = "health_check_log"
```

#### `src/data/db/repo/user_repo.py`

Extends `BaseRepo[User]` with: `get_by_email()`, `get_by_username()`, `get_by_id()`, `email_exists()`, `username_exists()`

#### `src/data/db/repo/health_check_log_repo.py`

Extends `BaseRepo[HealthCheckLog]` with: `get_recent(limit=10)`

### Infra Layer

#### `src/infra/cache/` — Cache implementations

**BaseCache:** encode/decode (JSON), get/set/delete/exists/clear; subclasses implement `_get_raw`/`_set_raw`/`_delete_raw`
**MemoryCache:** dict-based with TTL expiry; `clear(prefix)` support; O(n) scan
**RedisCache:** lazy async Redis connection via `redis.asyncio`; SCAN for prefix clear; `close()` method

#### `src/infra/event_bus/` — Event bus

**BaseEventBus:** publish/subscribe with `EventHandler` type alias
**MemoryEventBus:** per-topic handler list; sequential execution with try/except per handler

#### `src/infra/storage/` — File storage

**BaseFileStorage:** key validation (regex), content-type inference, path normalisation
**LocalFileStorage:** filesystem storage with path traversal protection
**S3FileStorage:** aioboto3-based S3/MinIO; lazy client initialisation; presigned URLs

### Module Layer

#### `src/module/health/` — Health check module

**Route:** `GET /api/v1/health/check` → `Success[HealthSchema]`

**HealthSchema:** version + db (status + version)

**HealthService:** checks DB health/version, persists to HealthCheckLog

#### `src/module/user/` — User module

**Routes (under `/api/v1/users`):**

| Method | Path | Description |
|---|---|---|
| POST | `/auth/register` | Create account → `UserSchema` (201) |
| POST | `/auth/login` | OAuth2 password flow → `TokenSchema` |
| POST | `/auth/refresh` | Rotate tokens |
| GET | `/auth/me` | Current user profile |
| GET | `/me` | Self-service read |
| PATCH | `/me` | Self-service update |

**Request schemas:**
- `RegisterRequest`: email (EmailStr), username (3-64 chars, alphanumeric+._-), password (12-128 chars), full_name (optional)
- `LoginRequest`: username (email or username), password
- `RefreshRequest`: refresh_token
- `UserUpdateRequest`: full_name (optional), password (optional)

**Response schemas:**
- `UserSchema`: id, email, username, full_name, role, is_active, created_at, updated_at
- `TokenSchema`: access_token, refresh_token, token_type, expires_in

**UserService methods:**
- `register(email, username, password, full_name?)`
- `authenticate(identifier, password)` — identifier is email or username
- `refresh(refresh_token)`
- `get_me(user_id)`
- `update_me(user_id, full_name?, password?)`

### Shared Layer

#### `src/shared/deps/` — FastAPI dependency injection

- **auth:** `get_current_user_id` (returns UUID or None), `require_user_id` (raises 401)
- **cache:** `get_cache()` → MemoryCache singleton (lru_cache)
- **common:** `PaginationParams`, `SortParams` dataclasses; `pagination_params()`, `sort_params()` dependency extractors
- **container:** `get_event_bus()` → MemoryEventBus singleton

#### `src/shared/middleware/`

- **ErrorBoundaryMiddleware:** catches all unhandled exceptions, returns graceful 500 JSON
- **LoggingMiddleware:** structured access log (method, path, status, duration, request_id, client_ip); skips `/metrics` and `/health/check`
- **RequestIdMiddleware:** propagates X-Request-ID header or generates UUID4
- **TimingMiddleware:** adds X-Response-Time header (ms)

**Order matters:** FastAPI applies last-added first (Starlette order).

#### `src/shared/observability/`

**Prometheus metrics:**
- `http_requests_total` (method, path, status) — Counter
- `http_request_duration_seconds` (method, path, status) — Histogram (0.005–10.0 buckets)
- `auth_login_success_total` — business signal Counter
- `render_metrics()` → (body, content_type) for `/metrics` endpoint
- `PrometheusMiddleware` — path templating via `request.scope['route'].path` to control cardinality

#### `src/shared/util/`

- **pagination:** `Page[T]` (items, page, page_size, total) with `total_pages`, `has_next()`, `has_prev()`; `Pagination` (page, page_size) with `offset`, `slice()`
- **sorting:** `parse_sort_string("-created_at,name")` → `["-created_at", "name"]`; `resolve_order_by()` with default fallback; regex validation prevents injection
- **validation:** `validate_password()` — OWASP 2024: ≥12 chars, printable ASCII, ≥3 of lowercase/uppercase/digit/symbol

### Task Layer (Background Jobs)

#### `src/task/worker.py` — ARQ worker setup

```python
@dataclass
class WorkerSettings:
    redis_host, redis_port, redis_db, poll_delay, max_jobs, burst

async def run_worker() -> None:  # blocking worker loop
```

Run via: `python -m src.task.worker`

#### `src/task/jobs/send_email.py` — Example job

```python
async def send_email(ctx, *, to: str, subject: str = "", body: str = "") -> bool
```

ARQ jobs must accept `ctx` as first argument. Enqueued by caller.

---

## Scripts (`scripts/`)

### `scripts/migrate.py`
```python
import asyncio
from src.data.db import run_migration

def main():
    asyncio.run(run_migration())
```

### `scripts/seed.py`
Seeds the database with demo data (admin@example.com, user@example.com). Idempotent via `get_or_create`.

### `scripts/lint.py`
Unified lint + format + type-check runner. Usage:
```
uv run python -m scripts.lint           # run all checks
uv run python -m scripts.lint --fix      # auto-fix (format + lint)
uv run python -m scripts.lint --check    # only check (no fix)
```

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/api/v1/health/check` | No | App + DB health status |
| POST | `/api/v1/users/auth/register` | No | Create account |
| POST | `/api/v1/users/auth/login` | No | Login → tokens |
| POST | `/api/v1/users/auth/refresh` | Refresh | Rotate tokens |
| GET | `/api/v1/users/auth/me` | Access | Current user |
| GET | `/api/v1/users/me` | Access | Self-service read |
| PATCH | `/api/v1/users/me` | Access | Self-service update |
| GET | `/metrics` | No | Prometheus scrape endpoint |
| GET | `/docs` | No | OpenAPI/Swagger UI |
| GET | `/openapi.json` | No | OpenAPI spec |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ENV` | — | Application environment (local/dev/prod/test) |
| `DEBUG` | — | Enable debug mode |
| `LOG_FORMAT` | `text` | Log output format (text/json) |
| `DB_SCHEMA` | — | Database schema label (postgresql) |
| `DB_HOST` | — | Database host |
| `DB_PORT` | — | Database port |
| `DB_USER` | — | Database user |
| `DB_PASSWORD` | — | Database password |
| `DB_NAME` | — | Database name |
| `CORS_ORIGINS` | `""` | Comma-separated CORS origins |
| `JWT_SECRET` | — | JWT signing secret (generate with `openssl rand -hex 32`) |
| `JWT_ALGORITHM` | `HS256` | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token lifetime |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token lifetime |
| `REDIS_HOST` | `redis` | Redis host |
| `REDIS_PORT` | `6379` | Redis port |
| `REDIS_DB` | `0` | Redis database index |
| `CACHE_TTL_DEFAULT` | `300` | Default cache TTL in seconds |
| `METRICS_ENABLED` | `true` | Enable Prometheus metrics |

---

## Quick Start

### Docker (recommended)
```bash
cp .env.example .env        # edit as needed
make up                     # builds + starts postgres + server
curl http://localhost:8000/api/v1/health/check
```

### Local (for development)
```bash
cp .env.example .env        # set DB_HOST=localhost
make install                # uv sync
make migrate                # apply Tortoise migrations
make run                    # uvicorn --reload
```

### Run tests
```bash
uv run pytest -vv --cov=src --cov-report=term-missing
```

---

## Adding a New Module

1. **Model** — `src/data/db/model/<name>.py` (subclass `Base`)
2. **Migration** — generate via Tortoise CLI or create manually
3. **Repo** — `src/data/db/repo/<name>_repo.py` (extends `BaseRepo[M]`)
4. **Route** — `src/module/<name>/route/<name>.py` (FastAPI router)
5. **Schema** — `src/module/<name>/schema/request.py` + `response.py` (subclass `BaseRequest`/`BaseResponse`)
6. **Service** — `src/module/<name>/service/<name>_service.py` (business logic)
7. **DI factory** — in `src/module/<name>/service/__init__.py`
8. **Register** — wire the router in `src/main.py`

### Wiring Checklist

```
src/data/db/model/<model>.py           # Tortoise model
src/data/db/model/__init__.py          # add import
src/data/db/repo/<repo>.py             # BaseRepo subclass
src/data/db/repo/__init__.py           # add import
src/module/<name>/schema/request.py    # request DTOs
src/module/<name>/schema/response.py   # response DTOs
src/module/<name>/schema/__init__.py   # re-exports
src/module/<name>/service/<svc>.py     # service class
src/module/<name>/service/__init__.py  # DI factory
src/module/<name>/route/<rt>.py        # FastAPI router
src/module/<name>/route/__init__.py    # aggregate sub-routers
src/module/<name>/__init__.py          # re-export router
src/main.py                            # include_router
```
