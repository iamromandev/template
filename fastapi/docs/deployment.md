# Deployment

## Prerequisites

- Docker & Docker Compose
- Environment variables configured (see `.env.production`)

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENV` | yes | — | `prod` |
| `DEBUG` | no | `false` | Enable debug mode |
| `LOG_FORMAT` | no | `text` | `json` in production |
| `DB_HOST` | yes | — | Database hostname |
| `DB_PORT` | yes | — | Database port |
| `DB_NAME` | yes | — | Database name |
| `DB_USER` | yes | — | Database user |
| `DB_PASSWORD` | yes | — | Database password |
| `JWT_SECRET` | yes | — | 256-bit random secret |
| `JWT_ALGORITHM` | no | `HS256` | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | no | `30` | Access token TTL |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | no | `7` | Refresh token TTL |
| `REDIS_HOST` | no | `redis` | Redis hostname |
| `REDIS_PORT` | no | `6379` | Redis port |
| `CORS_ORIGINS` | no | — | Comma-separated allowed origins |
| `METRICS_ENABLED` | no | `true` | Enable Prometheus `/metrics` |

## Database Migrations

Migrations run automatically on container start via the entrypoint script. To run manually:

```bash
docker compose exec server python -m src.scripts.migrate
```

## Health Checks

The production compose file includes a Docker healthcheck:

```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/check')"]
  interval: 30s
  timeout: 10s
  retries: 3
```

## Reverse Proxy

The production compose includes [Traefik](https://traefik.io/traefik/) as a reverse proxy with automatic SSL certificate management. Configure your domain in the `traefik` service labels.

## Monitoring

- **Metrics:** `GET /metrics` (Prometheus format)
- **Logs:** JSON structured logs via Loguru (`LOG_FORMAT=json`)
- **Health:** `GET /api/v1/health/check` (includes DB status probe)

## CI/CD Pipeline

See `.github/workflows/ci.yml` and `.github/workflows/cd.yml` for the automated pipeline:

1. **CI** (on PR/push): lint → typecheck → test → report
2. **CD** (on main push): build → push to registry → deploy to staging → deploy to production
