"""Database seeding — populate the database with starter / demo data.

Usage:

    uv run python -m scripts.seed

Run after migrations have been applied.  Idempotent (uses ``get_or_create``
wherever possible).
"""

from __future__ import annotations

import asyncio

from loguru import logger
from src.config import get_settings
from src.core.type import Env
from src.data.db import DB_CONFIG
from tortoise import Tortoise


async def seed() -> None:
    settings = get_settings()
    logger.info("Seeding database (env={})", settings.env)

    await Tortoise.init(config=DB_CONFIG)

    try:
        if settings.env == Env.LOCAL or settings.env == Env.DEV:
            await _seed_dev_data()
        logger.info("Seeding complete")
    except Exception:
        logger.exception("Seeding failed")
        raise
    finally:
        await Tortoise.close_connections()


async def _seed_dev_data() -> None:
    """Create demo data for local / dev environments."""
    from src.data.db.model.user import User

    admin_user, created = await User.get_or_create(
        email="admin@example.com",
        defaults={
            "username": "admin",
            "full_name": "Admin User",
            "hashed_password": "$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5yjq5xq5xq5xq5xq5xq5xq5y",
            "role": "admin",
            "is_active": True,
        },
    )
    if created:
        logger.info("Created admin user: {}", admin_user.email)
    else:
        logger.info("Admin user already exists: {}", admin_user.email)

    demo_user, created = await User.get_or_create(
        email="user@example.com",
        defaults={
            "username": "demo",
            "full_name": "Demo User",
            "hashed_password": "$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5yjq5xq5xq5xq5xq5xq5xq5y",
            "role": "user",
            "is_active": True,
        },
    )
    if created:
        logger.info("Created demo user: {}", demo_user.email)
    else:
        logger.info("Demo user already exists: {}", demo_user.email)


if __name__ == "__main__":
    asyncio.run(seed())


__all__ = ["seed"]
