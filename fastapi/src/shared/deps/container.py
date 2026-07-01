"""DI container — generic singleton/factory registrations.

Domain-specific factories (``get_<module>_service``) live in each
module's ``service/__init__.py``. This container holds **only** the
shared infra factories that have no upstream dependencies on
domain modules — currently a placeholder, to be filled as the project
grows (e.g. shared event-bus singleton).
"""

from __future__ import annotations

from functools import lru_cache

from src.infra.event_bus.memory_bus import MemoryEventBus


@lru_cache(maxsize=1)
def get_event_bus() -> MemoryEventBus:
    """Singleton event bus (in-memory for the template).

    Swap for ``RedisStreamsBus`` etc. when the deployment requires it.
    """
    return MemoryEventBus()


__all__ = ["get_event_bus"]
