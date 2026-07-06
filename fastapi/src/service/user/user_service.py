from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.auth.jwt import JWTIssuer
from src.auth.permission import Role
from src.core.error import Error
from src.core.security import hash_password, verify_password
from src.data.db.model.user import User
from src.data.repo.user_repo import UserRepo
from src.data.schema.user.response import TokenSchema, UserSchema


class UserService:
    def __init__(
        self,
        repo: UserRepo,
        jwt_issuer: JWTIssuer | None = None,
    ) -> None:
        self._repo = repo
        self._jwt = jwt_issuer or JWTIssuer()

    # --- registration -------------------------------------------------------

    async def register(
        self,
        *,
        email: str,
        username: str,
        password: str,
        full_name: str | None = None,
    ) -> UserSchema:
        normalized_email = email.lower()
        if await self._repo.email_exists(normalized_email):
            raise Error.conflict("Email already registered")
        if await self._repo.username_exists(username):
            raise Error.conflict("Username already taken")

        user = await self._repo.create(
            email=normalized_email,
            username=username,
            hashed_password=hash_password(password),
            full_name=full_name,
            role=Role.USER.value,
            is_active=True,
        )
        return self._to_schema(user)

    # --- authentication -----------------------------------------------------

    async def authenticate(self, *, identifier: str, password: str) -> TokenSchema:
        """``identifier`` may be username OR email."""
        user = await self._lookup(identifier)
        if user is None or not verify_password(password, user.hashed_password):
            raise Error.unauthorized("Invalid credentials")
        if not user.is_active:
            raise Error.forbidden("Account is disabled")

        user.last_login_at = datetime.now(UTC)
        await user.save(update_fields=["last_login_at"])

        pair = self._jwt.issue_pair(user.id)
        return TokenSchema(
            access_token=pair.access_token,
            refresh_token=pair.refresh_token,
            token_type=pair.token_type,
            expires_in=pair.expires_in,
        )

    async def refresh(self, *, refresh_token: str) -> TokenSchema:
        from src.config.config import get_settings

        settings = get_settings()
        from src.core.security import decode_token

        try:
            payload = decode_token(
                refresh_token,
                secret=settings.jwt_secret.get_secret_value(),
                algorithm=settings.jwt_algorithm,
                expected_type="refresh",
            )
        except Error:
            raise Error.unauthorized("Invalid refresh token") from None

        user = await self._repo.get_by_id(uuid.UUID(payload.sub))
        if user is None or not user.is_active:
            raise Error.unauthorized("User not found or disabled")

        pair = self._jwt.issue_pair(user.id)
        return TokenSchema(
            access_token=pair.access_token,
            refresh_token=pair.refresh_token,
            token_type=pair.token_type,
            expires_in=pair.expires_in,
        )

    # --- profile ------------------------------------------------------------

    async def get_me(self, user_id: uuid.UUID) -> UserSchema:
        user = await self._repo.get_by_id(user_id)
        if user is None:
            raise Error.not_found("User not found")
        return self._to_schema(user)

    async def update_me(
        self,
        user_id: uuid.UUID,
        *,
        full_name: str | None = None,
        password: str | None = None,
    ) -> UserSchema:
        updates: dict = {}
        if full_name is not None:
            updates["full_name"] = full_name
        if password is not None:
            updates["hashed_password"] = hash_password(password)

        if not updates:
            return await self.get_me(user_id)

        user = await self._repo.update(user_id, **updates)
        if user is None:
            raise Error.not_found("User not found")
        return self._to_schema(user)

    # --- helpers ------------------------------------------------------------

    async def _lookup(self, identifier: str) -> User | None:
        if "@" in identifier:
            return await self._repo.get_by_email(identifier)
        return await self._repo.get_by_username(identifier)

    @staticmethod
    def _to_schema(user: User) -> UserSchema:
        return UserSchema(
            id=user.id,
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            role=Role(user.role),
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
