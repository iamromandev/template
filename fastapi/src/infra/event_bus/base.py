"""Event-bus base — concrete buses implement ``_publish`` / ``_subscribe``.

For the template we ship only ``MemoryEventBus`` (single-process pub/sub).
Future: ``RedisStreamsBus``, ``KafkaBus``, ``NatsBus`` — drop-in via protocol.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

EventHandler = Callable[[dict[str, Any]], Awaitable[None]]


class BaseEventBus:
    async def _publish(self, topic: str, payload: dict[str, Any]) -> None:
        raise NotImplementedError

    async def _subscribe(self, topic: str, handler: EventHandler) -> None:
        raise NotImplementedError

    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        await self._publish(topic, payload)

    async def subscribe(self, topic: str, handler: EventHandler) -> None:
        await self._subscribe(topic, handler)


__all__ = ["BaseEventBus", "EventHandler"]
