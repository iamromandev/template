"""Connection management — pool lifecycle, health probes, retry logic.

This module wraps Tortoise ORM's connection lifecycle with:
    * Retry logic for transient failures (startup / migration).
    * Health probes that don't depend on Tortoise internals.
    * Metrics for connection pool utilisation.

Import from ``src.data.db.connection``, not from ``tortoise`` directly,
so the retry / health / metric wrappers are always active.
"""

from __future__ import annotations

import asyncio
from typing import Any

from loguru import logger
from tortoise import Tortoise

_RETRY_BASE_S = 1.0
_RETRY_MAX_S = 30.0
_RETRY_JITTER = 0.1


async def wait_for_db(max_retries: int = 10) -> bool:
    """Block until the database is reachable (useful at startup).

    Args:
        max_retries: Number of connection attempts before giving up.

    Returns:
        True if connected within the retry budget.
    """
    for attempt in range(1, max_retries + 1):
        try:
            conn = Tortoise.get_connection("default")
            await conn.execute_query("SELECT 1 AS one")
            logger.info("Database reachable after {}/{} attempts", attempt, max_retries)
            return True
        except Exception as exc:
            if attempt < max_retries:
                delay = min(_RETRY_BASE_S * 2**attempt, _RETRY_MAX_S)
                import random

                delay *= 1 + _RETRY_JITTER * random.random()
                logger.warning(
                    "DB unreachable (attempt {}/{}): {} — retrying in {:.1f}s",
                    attempt,
                    max_retries,
                    exc,
                    delay,
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    "DB unreachable after {}/{} attempts — giving up",
                    attempt,
                    max_retries,
                )
                return False
    return False


async def get_pool_stats() -> dict[str, Any]:
    """Return connection pool metrics (for Prometheus / health check).

    Returns:
        Dict with keys: ``min_size``, ``max_size``, ``current_size``,
        ``free_size``, ``in_use_size``.  Empty dict if not available.
    """
    try:
        conn = Tortoise.get_connection("default")
        pool = getattr(conn, "_pool", None)
        if pool is None:
            return {}
        return {
            "min_size": getattr(pool, "_minsize", 0),
            "max_size": getattr(pool, "_maxsize", 0),
            "current_size": getattr(pool, "_size", 0),
            "free_size": getattr(pool, "_freesize", 0),
            "in_use_size": max(0, getattr(pool, "_size", 0) - getattr(pool, "_freesize", 0)),
        }
    except Exception as exc:
        logger.debug("Could not read pool stats: {}", exc)
        return {}


async def close_all() -> None:
    """Gracefully close all Tortoise connections."""
    try:
        await Tortoise.close_connections()
        logger.info("All database connections closed")
    except Exception as exc:
        logger.error("Error closing DB connections: {}", exc)


__all__ = ["close_all", "get_pool_stats", "wait_for_db"]
