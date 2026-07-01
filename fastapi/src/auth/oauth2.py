"""OAuth2 password flow scheme.

Just the scheme object — plug it into routes via
``Depends(oauth2_scheme)`` to get the raw bearer token. Token validation
lives in ``src.deps.auth.get_current_user``.
"""

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


__all__ = ["oauth2_scheme"]
