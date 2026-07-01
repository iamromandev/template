"""Authentication dependencies.

* ``get_current_user_id`` — return ``uuid.UUID`` of the authenticated user,
  or ``None`` if the bearer token is absent / invalid.
* ``require_user_id`` — same as above, but raises 401 on miss.

Routes that **need** a user use ``require_user_id``; routes that are
public-but-personalized use ``get_current_user_id``.
"""

from __future__ import annotations

import uuid

from fastapi import Depends, Request

from src.auth.oauth2 import oauth2_scheme
from src.config.config import Settings, get_settings
from src.core.error import Error
from src.core.security import decode_token

_get_current_user_id_token_dep = Depends(oauth2_scheme)
_get_current_user_id_settings_dep = Depends(get_settings)


def get_current_user_id(
    request: Request,
    token: str | None = _get_current_user_id_token_dep,
    settings: Settings = _get_current_user_id_settings_dep,
) -> uuid.UUID | None:
    """Return user id from the access token, or ``None`` if unauthenticated."""
    if not token:
        return None
    try:
        payload = decode_token(
            token,
            secret=settings.jwt_secret.get_secret_value(),
            algorithm=settings.jwt_algorithm,
            expected_type="access",
        )
    except Error:
        return None
    request.state.user_id = payload.sub
    return uuid.UUID(payload.sub)


_require_user_id_dep = Depends(get_current_user_id)


def require_user_id(
    user_id: uuid.UUID | None = _require_user_id_dep,
) -> uuid.UUID:
    """Strict variant — raises 401 if no valid token is present."""
    if user_id is None:
        raise Error.unauthorized("Authentication required")
    return user_id


__all__ = ["get_current_user_id", "require_user_id"]
