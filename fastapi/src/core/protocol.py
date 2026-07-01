"""Abstract protocols for shared infra.

These ``Protocol`` classes define the contracts that infra
adapters must satisfy. Services depend on these protocols (not on
concrete implementations), which lets you swap Redis for in-memory,
or local-filesystem for S3, without touching service code.

Why Protocol and not ABC?
    * Structural typing — adapters don't need to inherit.
    * No runtime cost (type-checker only).
    * Aligns with ADR-005.
"""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any, Protocol, TypeVar, runtime_checkable

from tortoise import models, queryset
from tortoise.query_utils import Prefetch

M = TypeVar("M", bound="models.Model")


@runtime_checkable
class Repository(Protocol[M]):
    """Generic repository contract for any Tortoise model."""

    async def count(self, *args: Any, **kwargs: Any) -> int: ...

    async def exists(self, *args: Any, **kwargs: Any) -> bool: ...

    async def create(self, **kwargs: Any) -> M: ...

    async def get_or_create(self, **kwargs: Any) -> tuple[M, bool]: ...

    async def get_or_none(self, **kwargs: Any) -> M | None: ...

    async def get_by_id(
        self,
        id: uuid.UUID,
        select_related: str | Sequence[str] | None = None,
        prefetch_related: str | Sequence[str] | None = None,
        annotations: dict[str, Any] | None = None,
    ) -> M | None: ...

    async def get_one(
        self,
        *args: Any,
        order_by: str | None = None,
        **kwargs: Any,
    ) -> M | None: ...

    async def get_many(
        self,
        *args: Any,
        order_by: str | None = None,
        limit: int | None = None,
        **kwargs: Any,
    ) -> list[M]: ...

    async def get_paginated(
        self,
        *args: Any,
        order_by: str | None = None,
        page: int = 1,
        page_size: int = 10,
        **kwargs: Any,
    ) -> tuple[list[M], dict[str, int]]: ...

    async def update(self, target: uuid.UUID | M, **kwargs: Any) -> M | None: ...

    async def delete(self, target: uuid.UUID | M) -> bool: ...


@runtime_checkable
class Cache(Protocol):
    """Cache backend contract (Redis / in-memory / etc.).

    ``set`` uses an async TTL in seconds. ``get`` returns ``None`` on
    miss. ``delete`` returns ``True`` if a key was removed.
    """

    async def get(self, key: str) -> str | None: ...

    async def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int | None = None,
    ) -> None: ...

    async def delete(self, key: str) -> bool: ...

    async def exists(self, key: str) -> bool: ...

    async def clear(self, prefix: str | None = None) -> int: ...


@runtime_checkable
class EventBus(Protocol):
    """Pub/sub contract (in-memory / Redis Streams / NATS / Kafka)."""

    async def publish(self, topic: str, payload: dict[str, Any]) -> None: ...

    async def subscribe(
        self,
        topic: str,
        handler: Any,
    ) -> None: ...


@runtime_checkable
class FileStorage(Protocol):
    """Object/file storage contract (local / S3 / MinIO)."""

    async def put(
        self,
        key: str,
        data: bytes,
        content_type: str | None = None,
    ) -> str: ...

    async def get(self, key: str) -> bytes: ...

    async def delete(self, key: str) -> bool: ...

    async def url(self, key: str, expires_in: int = 3600) -> str: ...


# Re-export so other modules can do `from src.core.protocol import Prefetch` etc.
__all__ = [
    "Cache",
    "EventBus",
    "FileStorage",
    "Prefetch",
    "Repository",
    "queryset",
]
