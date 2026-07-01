# FastAPI Template

Minimal FastAPI starter with PostgreSQL + Tortoise ORM. A single healthcheck
endpoint, one empty initial migration, and the four-tier architecture
(Route → Service → Repo → Model) ready to grow on.

## Stack

- **uv** (package manager), Python `>=3.14.3`
- **FastAPI** + uvicorn (uvloop)
- **Tortoise ORM** (asyncpg) with built-in migrations
- **PostgreSQL** (plain `postgres` image)
- **loguru** logging, **ruff** lint

## Quick start

```bash
cp .env.example .env        # adjust as needed
make up                     # postgres + server via docker-compose
curl http://localhost:8000/health/check
```

Or run locally against a Postgres on the host (set `DB_HOST=localhost`):

```bash
make install                # uv sync
make migrate                # apply migrations
make run                    # uvicorn with reload
```

## Endpoint

`GET /health/check` → `Success[HealthSchema]` envelope reporting app version and
database status/version.

## Adding a feature

Follow the four-tier flow: **Model** (`src/data/db/model/`, subclass
`core.base.Base`) → generate a **migration** → **Repo** (`src/data/repo/`, use
`BaseRepo[M]`) → **Schema** (`src/data/schema/`, subclass `BaseSchema`) →
**Service** (`src/service/`, subclass `BaseService` + a DI factory) → **Route**
(`src/route/`, register in `src/route/__init__.py`).

See `docs/template.md` for the full build guide this project was generated from.
