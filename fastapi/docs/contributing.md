# Contributing

## Setup

```bash
# Prerequisites
uv sync --group dev

# Install pre-commit hooks
pre-commit install
```

## Development Workflow

```bash
# Run development server with auto-reload
make run

# Or via Docker
make up

# View logs
make logs
```

## Code Quality

```bash
# Lint + format + typecheck
make check

# Format only
make format

# Lint only
make lint

# Typecheck only
make typecheck
```

Uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting (line length 100, Python 3.14 target) and [ty](https://github.com/radiac/ty) for type checking.

## Adding a New Module

```bash
# Create the module structure
mkdir -p src/<module>/{model,repo,schema,service,route}
```

### Wiring Checklist

1. **Model** — subclass `src.core.base.Base` in `src/<module>/model/<model>.py`
2. **Repo** — subclass `BaseRepo[M]` in `src/<module>/repo/<model>_repo.py`
3. **Schemas** — subclass `BaseRequest` / `BaseResponse` in `src/<module>/schema/`
4. **Service** — subclass `BaseService` in `src/<module>/service/<module>_service.py`
5. **DI Factory** — add `get_<module>_service()` in `src/<module>/service/__init__.py`
6. **Routes** — create `APIRouter` in `src/<module>/route/`
7. **Register model** in `src/data/db/__init__.py` (`DB_CONFIG["apps"]["model"]["models"]`)
8. **Re-export model** in `src/data/db/model/__init__.py`
9. **Create migration** in `src/data/db/migration/`
10. **Register router** in `src/route/__init__.py`

### Module Template

See `src/health/` or `src/user/` for reference implementations.

## Pull Request Guidelines

1. Branch from `main`, name as `feature/` or `fix/`
2. Run `make check` before pushing
3. Keep PRs focused — one feature/fix per PR
4. Update docs if adding or changing public API
