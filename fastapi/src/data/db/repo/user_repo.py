"""User repository — adds email / username lookups on top of BaseRepo."""

from __future__ import annotations

import uuid

from src.core.base import BaseRepo
from src.data.db.model.user import User


class UserRepo(BaseRepo[User]):
    def __init__(self) -> None:
        super().__init__(User)

    async def get_by_email(self, email: str) -> User | None:
        return await self.get_or_none(email=email.lower())

    async def get_by_username(self, username: str) -> User | None:
        return await self.get_or_none(username=username)

    async def get_by_id(self, user_id: uuid.UUID, **kwargs) -> User | None:  # type: ignore[override]
        return await super().get_by_id(user_id, **kwargs)

    async def email_exists(self, email: str) -> bool:
        return await self.exists(email=email.lower())

    async def username_exists(self, username: str) -> bool:
        return await self.exists(username=username)


__all__ = ["UserRepo"]
