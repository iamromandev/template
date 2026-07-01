"""Redis cache — async client (redis-py asyncio).

Connection is lazy; the first ``get`` / ``set`` triggers it. On Redis
failure we log and propagate; we **don't** silently fall back to memory
(better to fail loudly in prod).

Requires ``redis>=5`` (already pinned in pyproject).
"""

from __future__ import annotations

from loguru import logger
from redis.asyncio import Redis, from_url

from src.config.config import Settings, get_settings
from src.infra.cache.base import BaseCache


class RedisCache(BaseCache):
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        url: str | None = None,
        default_ttl: int | None = None,
    ) -> None:
        settings = settings or get_settings()
        super().__init__(
            default_ttl=default_ttl if default_ttl is not None else settings.cache_ttl_default,
        )
        self._client: Redis | None = None
        self._url = url or self._build_url(settings)

    @staticmethod
    def _build_url(settings: Settings) -> str:
        password = f":{settings.redis_password.get_secret_value()}@" if settings.redis_password else ""
        return f"redis://{password}{settings.redis_host}:{settings.redis_port}/{settings.redis_db}"

    async def _ensure(self) -> Redis:
        if self._client is None:
            try:
                self._client = from_url(self._url, encoding="utf-8", decode_responses=True)
                await self._client.ping()
                logger.info("RedisCache connected to {}", self._url)
            except Exception as e:  # pragma: no cover — infra error
                logger.error("RedisCache connection failed: {}", e)
                raise
        return self._client

    async def _get_raw(self, key: str) -> str | None:
        client = await self._ensure()
        return await client.get(key)

    async def _set_raw(self, key: str, value: str, ttl_seconds: int | None) -> None:
        client = await self._ensure()
        if ttl_seconds:
            await client.set(key, value, ex=ttl_seconds)
        else:
            await client.set(key, value)

    async def _delete_raw(self, key: str) -> bool:
        client = await self._ensure()
        deleted = await client.delete(key)
        return bool(deleted)

    async def clear(self, prefix: str | None = None) -> int:
        client = await self._ensure()
        if prefix is None:
            await client.flushdb()
            return -1
        # SCAN is non-blocking even with large keyspaces
        keys: list[str] = []
        async for key in client.scan_iter(match=f"{prefix}*"):
            keys.append(key)
        if not keys:
            return 0
        await client.delete(*keys)
        return len(keys)

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None


__all__ = ["RedisCache"]
