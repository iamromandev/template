"""Role-based permission checks.

Two enums:
    * ``Role``    — coarse-grained user role (user / admin / superadmin).
    * ``Permission`` — fine-grained action (user:read, user:write, ...).

Use ``require_role(Role.ADMIN)`` as a route deps to gate access.
Use ``require_permission(Permission.USER_WRITE)`` for finer control.

A real RBAC system would map roles → permissions in the DB. For the
template, ``Role.ADMIN`` is treated as having all permissions.
"""

from __future__ import annotations

import uuid
from enum import StrEnum

from fastapi import Depends

from src.auth.oauth2 import oauth2_scheme
from src.core.error import Error
from src.core.type import Code, ErrorType
from src.shared.deps.auth import get_current_user_id as _get_current_user_id


class Role(StrEnum):
    USER = "user"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"


class Permission(StrEnum):
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"


_ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.USER: {Permission.USER_READ},
    Role.ADMIN: {Permission.USER_READ, Permission.USER_WRITE, Permission.ADMIN_READ},
    Role.SUPERADMIN: set(Permission),
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in _ROLE_PERMISSIONS.get(role, set())


class CurrentPrincipal:
    """Identity attached to a request after JWT validation."""

    __slots__ = ("role", "user_id")

    def __init__(self, user_id: uuid.UUID, role: Role = Role.USER) -> None:
        self.user_id = user_id
        self.role = role


_require_role_token_dep = Depends(oauth2_scheme)
_require_role_user_id_dep = Depends(_get_current_user_id)


def require_role(*allowed: Role):
    """Dependency factory: 401 if not authenticated, 403 if wrong role."""

    async def _checker(
        token: str | None = _require_role_token_dep,
        user_id: uuid.UUID | None = _require_role_user_id_dep,
    ) -> CurrentPrincipal:
        if user_id is None or token is None:
            raise Error.unauthorized("Authentication required")
        # In a real app, fetch the user's role from the DB. For the
        # template we default to USER and let route-level checks escalate.
        principal = CurrentPrincipal(user_id=user_id, role=Role.USER)
        if principal.role not in allowed:
            raise Error.forbidden(
                f"Role '{principal.role}' not in required: {sorted(r.value for r in allowed)}",
            )
        return principal

    return _checker


_require_permission_principal_dep = Depends(
    require_role(Role.USER, Role.ADMIN, Role.SUPERADMIN),
)


def require_permission(permission: Permission):
    """Dependency factory: 401 if not authenticated, 403 if missing perm."""

    async def _checker(
        principal: CurrentPrincipal = _require_permission_principal_dep,
    ) -> CurrentPrincipal:
        if not has_permission(principal.role, permission):
            raise Error(
                code=Code.FORBIDDEN,
                message=f"Missing permission: {permission.value}",
                error_type=ErrorType.AUTHORIZATION_ERROR,
            )
        return principal

    return _checker


__all__ = [
    "CurrentPrincipal",
    "Permission",
    "Role",
    "has_permission",
    "require_permission",
    "require_role",
]
