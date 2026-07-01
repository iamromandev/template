"""Pagination helpers — offset-based (page/page_size) and cursor-based.

The ``BaseRepo.get_paginated`` already does offset-based pagination at the
repo layer. These helpers are for code that paginates **outside** the
repo (e.g. when consolidating multiple sources).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class Page[T]:
    items: list[T]
    page: int
    page_size: int
    total: int

    @property
    def total_pages(self) -> int:
        return (self.total + self.page_size - 1) // self.page_size if self.page_size else 0

    def has_next(self) -> bool:
        return self.page < self.total_pages

    def has_prev(self) -> bool:
        return self.page > 1


@dataclass(frozen=True)
class Pagination:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    def slice(self, items: list[T]) -> list[T]:
        return items[self.offset : self.offset + self.page_size]


__all__ = ["Page", "Pagination"]
