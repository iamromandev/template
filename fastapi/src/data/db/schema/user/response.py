from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import EmailStr, Field
from src.auth.permission import Role
from src.core.schema import BaseResponse


class UserSchema(BaseResponse):
    id: Annotated[uuid.UUID, ...]
    email: Annotated[EmailStr, ...]
    username: Annotated[str, ...]
    full_name: Annotated[str | None, Field(default=None)]
    role: Annotated[Role, Field(default=Role.USER)]
    is_active: Annotated[bool, Field(default=True)]
    created_at: Annotated[datetime, ...]
    updated_at: Annotated[datetime, ...]


class TokenSchema(BaseResponse):
    access_token: Annotated[str, ...]
    refresh_token: Annotated[str, ...]
    token_type: Annotated[str, Field(default="bearer")]
    expires_in: Annotated[int, Field(description="Access-token lifetime in seconds")]
