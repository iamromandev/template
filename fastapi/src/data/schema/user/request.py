from __future__ import annotations

from typing import Annotated

from pydantic import EmailStr, Field
from src.core.schema import BaseRequest


class RegisterRequest(BaseRequest):
    email: Annotated[EmailStr, Field(description="Unique account email")]
    username: Annotated[str, Field(min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_.-]+$")]
    password: Annotated[str, Field(min_length=12, max_length=128, description="≥12 chars, mixed classes")]
    full_name: Annotated[str | None, Field(default=None, max_length=255)] = None


class LoginRequest(BaseRequest):
    username: Annotated[
        str,
        Field(
            description="Username OR email — both are accepted",
        ),
    ]
    password: Annotated[str, Field(min_length=1)]


class RefreshRequest(BaseRequest):
    refresh_token: Annotated[str, Field(min_length=10)]


class UserUpdateRequest(BaseRequest):
    full_name: Annotated[str | None, Field(default=None, max_length=255)] = None
    password: Annotated[str | None, Field(default=None, min_length=12, max_length=128)] = None
