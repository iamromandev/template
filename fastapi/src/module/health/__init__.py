"""Health module — self-contained domain module.

This module demonstrates the standard project pattern where each domain
owns its own model, repo, schema, service, and route layers.

Pattern for adding a new module (e.g. `item`):
    src/item/
    ├── model/          # Tortoise models
    ├── repo/           # Data access layer
    ├── schema/         # Request/response DTOs
    ├── service/        # Business logic
    └── route/          # HTTP endpoints
"""

from src.module.health.route import router as health_router

__all__ = ["health_router"]
