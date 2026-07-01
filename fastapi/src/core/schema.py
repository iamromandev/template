"""Split DTO bases — explicit ``BaseRequest`` and ``BaseResponse``.

Why a split?
    * ``BaseSchema`` stays for shared concerns (logging, ``to_dict``).
    * Inbound DTOs (``BaseRequest``) document what the API accepts.
    * Outbound DTOs (``BaseResponse``) document what the API returns.
    * Type-checkers + readers see intent at the call site:
      ``class LoginRequest(BaseRequest)`` is clearer than
      ``class LoginRequest(BaseSchema)``.

The default ``model_config`` mirrors ``BaseSchema`` (``from_attributes=True``)
so existing modules don't break.
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import ConfigDict, Field

from src.core.base import BaseSchema


class BaseRequest(BaseSchema):
    """Base for inbound DTOs (request bodies / query params)."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class BaseResponse(BaseSchema):
    """Base for outbound DTOs (API response bodies)."""

    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseSchema):
    """Pagination metadata emitted alongside paginated responses."""

    page: Annotated[int, Field(default=1, ge=1)]
    page_size: Annotated[int, Field(default=10, ge=1, le=100)]
    total: Annotated[int, Field(default=0, ge=0)]
    total_pages: Annotated[int, Field(default=0, ge=0)]

    @classmethod
    def build(
        cls,
        *,
        page: int,
        page_size: int,
        total: int,
    ) -> PaginationMeta:
        total_pages = (total + page_size - 1) // page_size if page_size else 0
        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=total_pages,
        )


__all__ = ["BaseRequest", "BaseResponse", "PaginationMeta"]


def _example() -> dict[str, Any]:
    """Used in tests to sanity-check that imports resolve."""
    return PaginationMeta().model_dump()
