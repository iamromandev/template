"""Cache deps.

Returns a singleton ``Cache`` implementation. Defaults to in-memory
unless ``ENV=prod`` (or ``CACHE_BACKEND=redis`` is set, future work).
"""

from __future__ import annotations

from functools import lru_cache

from src.config.config import Settings, get_settings
from src.core.protocol import Cache
from src.infra.cache.memory_cache import MemoryCache


@lru_cache(maxsize=1)
def get_cache() -> Cache:
    settings: Settings = get_settings()
    # Default to memory cache. Swap to RedisCache once infra/redis is wired.
    return MemoryCache(default_ttl=settings.cache_ttl_default)


__all__ = ["get_cache"]
