"""Security primitives — password hashing and JWT helpers.

Why bcrypt directly (not passlib)?
    * passlib's bcrypt backend lags behind the upstream ``bcrypt`` lib
      and has known compatibility issues on Python 3.13+ / 3.14.
    * ``bcrypt`` alone is a small, well-maintained C/Rust extension with
      official wheels for current Python versions.

Why PyJWT?
    * Pure Python (with optional ``crypto`` extra for RS256/ES256).
    * De-facto standard for JWT in Python.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt
from pydantic import BaseModel

from src.core.error import Error
from src.core.type import Code, ErrorType

# --- password hashing --------------------------------------------------------

_BCRYPT_ROUNDS = 12  # 2^12 ≈ 250ms on modern hardware — OWASP 2024 minimum


def hash_password(plain: str) -> str:
    """Return a bcrypt hash for ``plain``."""
    if not plain:
        msg = "password must not be empty"
        raise Error.bad_request(msg)
    salt = bcrypt.gensalt(rounds=_BCRYPT_ROUNDS)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time verify; ``False`` on any decoding error."""
    if not plain or not hashed:
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# --- JWT helpers -------------------------------------------------------------

JWT_ALGORITHM_DEFAULT = "HS256"


class TokenPayload(BaseModel):
    """Standard claims our app understands.

    ``sub`` is the user id (UUID-as-string). ``type`` distinguishes
    access vs refresh tokens so a refresh token can't be used as an
    access token by accident.
    """

    sub: str
    type: str = "access"
    iat: int
    exp: int
    jti: str


def encode_token(
    *,
    subject: str | uuid.UUID,
    secret: str,
    algorithm: str = JWT_ALGORITHM_DEFAULT,
    expires_in: timedelta,
    token_type: str = "access",
) -> str:
    """Issue a JWT for ``subject`` (user id)."""
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_in).timestamp()),
        "jti": uuid.uuid4().hex,
    }
    return jwt.encode(payload, secret, algorithm=algorithm)


def decode_token(
    token: str,
    *,
    secret: str,
    algorithm: str = JWT_ALGORITHM_DEFAULT,
    expected_type: str = "access",
) -> TokenPayload:
    """Decode + validate ``token``. Raises ``Error`` on any failure.

    The mapping is:
        * ``ExpiredSignatureError``  → ``TOKEN_EXPIRED``  (401)
        * ``InvalidTokenError``      → ``TOKEN_INVALID``  (401)
        * wrong ``type`` claim       → ``TOKEN_INVALID``  (401)
    """
    try:
        raw = jwt.decode(token, secret, algorithms=[algorithm])
    except jwt.ExpiredSignatureError as e:
        raise Error(
            code=Code.UNAUTHORIZED,
            message="Token has expired",
            error_type=ErrorType.TOKEN_EXPIRED,
        ) from e
    except jwt.InvalidTokenError as e:
        raise Error(
            code=Code.UNAUTHORIZED,
            message="Invalid token",
            error_type=ErrorType.TOKEN_INVALID,
        ) from e

    if raw.get("type") != expected_type:
        raise Error(
            code=Code.UNAUTHORIZED,
            message=f"Expected token of type '{expected_type}', got '{raw.get('type')}'",
            error_type=ErrorType.TOKEN_INVALID,
        )

    return TokenPayload.model_validate(raw)


__all__ = [
    "JWT_ALGORITHM_DEFAULT",
    "TokenPayload",
    "decode_token",
    "encode_token",
    "hash_password",
    "verify_password",
]
