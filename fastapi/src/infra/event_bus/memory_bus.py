"""In-memory event bus — single-process pub/sub.

Handlers run sequentially per topic. Failures in one handler don't
cancel the others (each is wrapped in try/except + log).
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from loguru import logger

from src.infra.event_bus.base import BaseEventBus, EventHandler


class MemoryEventBus(BaseEventBus):
    def __init__(self) -> None:
        self._subs: dict[str, list[EventHandler]] = defaultdict(list)

    async def _publish(self, topic: str, payload: dict[str, Any]) -> None:
        for handler in list(self._subs.get(topic, [])):
            try:
                await handler(payload)
            except Exception as e:
                logger.exception("EventBus handler failed for topic '{}': {}", topic, e)

    async def _subscribe(self, topic: str, handler: EventHandler) -> None:
        self._subs[topic].append(handler)


__all__ = ["MemoryEventBus"]
