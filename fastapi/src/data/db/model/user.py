"""User model — accounts, credentials, profile basics."""

from __future__ import annotations

import uuid

from tortoise import fields

from src.auth.permission import Role
from src.core.base import Base


class User(Base):
    """A registered account.

    Soft-delete + timestamps come from ``Base``. Email is unique; the
    case-folding invariant is enforced at the service layer (lower-case
    before lookup / insert).
    """

    email = fields.CharField(max_length=255, unique=True, db_index=True)
    username = fields.CharField(max_length=64, unique=True, db_index=True)
    hashed_password = fields.CharField(max_length=255)
    full_name = fields.CharField(max_length=255, null=True)
    role = fields.CharField(
        max_length=32,
        default=Role.USER.value,
        description="Role: user | admin | superadmin",
    )
    is_active = fields.BooleanField(default=True)
    last_login_at = fields.DatetimeField(null=True)

    class Meta:
        table = "user"

    @property
    def role_enum(self) -> Role:
        return Role(self.role)


__all__ = ["User"]


def _touch_last_login(user_id: uuid.UUID) -> None:  # pragma: no cover — helper
    """Convenience hook for service code; not a model method."""
    pass
