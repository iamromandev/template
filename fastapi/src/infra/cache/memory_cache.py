"""In-memory cache — process-local, no external deps.

Use for:
    * unit tests
    * local development without Redis
    * single-instance deployments where a shared cache isn't required

Not safe for multi-process deployments. ``clear`` is O(n).
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from src.infra.cache.base import BaseCache


@dataclass
class _Entry:
    value: str
    expires_at: float  # monotonic seconds


class MemoryCache(BaseCache):
    def __init__(self, default_ttl: int = 300) -> None:
        super().__init__(default_ttl=default_ttl)
        self._store: dict[str, _Entry] = {}

    def _is_expired(self, entry: _Entry) -> bool:
        return entry.expires_at <= time.monotonic()

    async def _get_raw(self, key: str) -> str | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if self._is_expired(entry):
            self._store.pop(key, None)
            return None
        return entry.value

    async def _set_raw(self, key: str, value: str, ttl_seconds: int | None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        self._store[key] = _Entry(
            value=value,
            expires_at=time.monotonic() + ttl,
        )

    async def _delete_raw(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    async def clear(self, prefix: str | None = None) -> int:
        if prefix is None:
            count = len(self._store)
            self._store.clear()
            return count
        keys = [k for k in self._store if k.startswith(prefix)]
        for k in keys:
            self._store.pop(k, None)
        return len(keys)


__all__ = ["MemoryCache"]
