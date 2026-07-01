"""Async-cache base class.

Concrete subclasses (``MemoryCache``, ``RedisCache``) implement the
actual ``get`` / ``set`` / ``delete`` methods. This base exists to
share the ``encode`` / ``decode`` helpers and the common TTL handling.
"""

from __future__ import annotations

import json
from typing import Any


class BaseCache:
    """Subclasses must implement ``_get_raw`` / ``_set_raw`` / ``_delete_raw``."""

    def __init__(self, default_ttl: int = 300) -> None:
        self._default_ttl = default_ttl

    # --- subclass hooks ---
    async def _get_raw(self, key: str) -> str | None:
        raise NotImplementedError

    async def _set_raw(self, key: str, value: str, ttl_seconds: int | None) -> None:
        raise NotImplementedError

    async def _delete_raw(self, key: str) -> bool:
        raise NotImplementedError

    # --- public API ---
    @staticmethod
    def encode(value: Any) -> str:
        """JSON-encode any JSON-serialisable value (Pydantic models too via ``mode_json``)."""
        if hasattr(value, "model_dump_json"):
            return value.model_dump_json()  # type: ignore[attr-defined]
        if hasattr(value, "model_dump"):
            return json.dumps(value.model_dump(), default=str)  # type: ignore[attr-defined]
        return json.dumps(value, default=str)

    @staticmethod
    def decode(value: str) -> Any:
        return json.loads(value)

    async def get(self, key: str) -> str | None:
        return await self._get_raw(key)

    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int | None = None,
    ) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        await self._set_raw(key, value, ttl)

    async def delete(self, key: str) -> bool:
        return await self._delete_raw(key)

    async def exists(self, key: str) -> bool:
        return (await self._get_raw(key)) is not None

    async def clear(self, prefix: str | None = None) -> int:
        """Subclasses override for prefix-aware clearing."""
        raise NotImplementedError


__all__ = ["BaseCache"]
