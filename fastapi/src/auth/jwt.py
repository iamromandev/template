"""JWT issuance facade.

Wraps the ``encode_token`` core helper with the application settings,
so callers don't have to plumb ``secret`` / ``algorithm`` everywhere.
The refresh token flow (rotate on use) lives here too.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import timedelta

from src.config.config import Settings, get_settings
from src.core.security import encode_token


@dataclass(frozen=True)
class IssuedTokenPair:
    """What ``JWTIssuer.issue_pair`` returns."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 0  # seconds until access_token expires


class JWTIssuer:
    """Stateless issuer — instantiate freely; safe to share."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    @property
    def algorithm(self) -> str:
        return self._settings.jwt_algorithm

    def issue_access(self, user_id: uuid.UUID | str) -> str:
        return encode_token(
            subject=user_id,
            secret=self._settings.jwt_secret.get_secret_value(),
            algorithm=self.algorithm,
            expires_in=timedelta(minutes=self._settings.jwt_access_token_expire_minutes),
            token_type="access",
        )

    def issue_refresh(self, user_id: uuid.UUID | str) -> str:
        return encode_token(
            subject=user_id,
            secret=self._settings.jwt_secret.get_secret_value(),
            algorithm=self.algorithm,
            expires_in=timedelta(days=self._settings.jwt_refresh_token_expire_days),
            token_type="refresh",
        )

    def issue_pair(self, user_id: uuid.UUID | str) -> IssuedTokenPair:
        return IssuedTokenPair(
            access_token=self.issue_access(user_id),
            refresh_token=self.issue_refresh(user_id),
            expires_in=self._settings.jwt_access_token_expire_minutes * 60,
        )


jwt_issuer = JWTIssuer()
