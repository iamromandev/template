"""Common FastAPI dependencies: pagination, sorting.

These are plain dataclasses — they plug into ``Depends(...)`` so each
route handler can declare them as typed parameters:

    @router.get("/items")
    async def list_items(
        page: Annotated[PaginationParams, Depends(pagination_params)],
        sort: Annotated[SortParams, Depends(sort_params)],
    ):
        ...
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Query


@dataclass(frozen=True)
class PaginationParams:
    page: int
    page_size: int


@dataclass(frozen=True)
class SortParams:
    sort: str | None  # e.g. "-created_at,name"


def pagination_params(
    page: Annotated[int, Query(default=1, ge=1, description="1-indexed page")] = 1,
    page_size: Annotated[int, Query(default=10, ge=1, le=100, description="Items per page")] = 10,
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


def sort_params(
    sort: Annotated[
        str | None,
        Query(
            default=None,
            description=("Comma-separated fields. Prefix '-' for descending. Example: '-created_at,name'"),
        ),
    ] = None,
) -> SortParams:
    return SortParams(sort=sort)


__all__ = ["PaginationParams", "SortParams", "pagination_params", "sort_params"]
