"""Sort-string parsing.

Accepts ``-created_at,name`` (Tortoise style):
    * ``-foo`` → descending
    * ``foo``  → ascending
    * Multiple fields → comma-separated, applied left-to-right
"""

from __future__ import annotations

import re

# Field names: snake_case identifiers only — prevents injection
_FIELD_RE = re.compile(r"^-?[a-zA-Z_][a-zA-Z0-9_]*$")


def parse_sort_string(raw: str | None) -> list[str]:
    """Validate and split ``raw`` into a list of Tortoise ``order_by`` strings."""
    if not raw:
        return []
    fields = [s.strip() for s in raw.split(",") if s.strip()]
    for field in fields:
        if not _FIELD_RE.match(field):
            msg = f"Invalid sort field: '{field}'"
            raise ValueError(msg)
    return fields


def resolve_order_by(raw: str | None, *, default: list[str] | None = None) -> list[str]:
    """Return parsed order_by, falling back to ``default`` on empty input."""
    parsed = parse_sort_string(raw)
    return parsed if parsed else (default or [])


__all__ = ["parse_sort_string", "resolve_order_by"]
