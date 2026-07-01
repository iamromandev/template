"""Loguru configuration.

Two formats:
    * ``local``  — colored, single-line, includes source line numbers.
    * non-local  — JSON, structured, ready for log aggregators.

Override via ``LOG_FORMAT`` env var (``json`` | ``text``).
"""

from __future__ import annotations

import json
import sys
from typing import Any

from loguru import logger

from src.config.config import get_settings

_LOG_LEVELS = {
    "trace": 5,
    "debug": 10,
    "info": 20,
    "success": 25,
    "warning": 30,
    "error": 40,
    "critical": 50,
}


def _resolve_level() -> str:
    settings = get_settings()
    if settings.debug:
        return "debug"
    return "info"


def _resolve_sink() -> str:
    """Return loguru format string for current env."""
    settings = get_settings()
    if settings.log_format == "json":
        return (
            "{{"
            '"timestamp":"{{time:YYYY-MM-DDTHH:mm:ss.SSSZ}}",'
            '"level":"{level}",'
            '"logger":"{name}",'
            '"message":"{message}",'
            '"module":"{module}",'
            '"function":"{function}",'
            '"line":{line}'
            "}}"
        )
    return (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )


def configure_logging() -> None:
    """Idempotently configure the root loguru sink."""
    logger.remove()
    logger.add(
        sys.stdout,
        level=_resolve_level(),
        format=_resolve_sink(),
        serialize=False,
        enqueue=False,
        backtrace=True,
        diagnose=False,
    )


__all__ = ["configure_logging", "logger"]


def _safe_json_default(obj: Any) -> Any:  # pragma: no cover — helper
    return str(obj)


def json_log(record: dict[str, Any]) -> str:  # pragma: no cover — helper
    """Helper for places that need a pre-serialized JSON line."""
    return json.dumps(record, default=_safe_json_default)
