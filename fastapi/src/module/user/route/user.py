"""User CRUD routes — admin-only in production, but ``/me`` is open to any user.

Note: this template only demonstrates the ``/me`` self-service surface.
Full admin CRUD is intentionally left as an exercise for the consumer
to keep the template focused.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.core.success import Success
from src.module.user.schema.request import UserUpdateRequest
from src.module.user.schema.response import UserSchema
from src.module.user.service import UserService, get_user_service
from src.shared.deps.auth import require_user_id

router = APIRouter()


@router.get(
    path="/me",
    response_model=Success[UserSchema],
    summary="Self-service: read the authenticated user",
)
async def read_me(
    user_id: Annotated[uuid.UUID, Depends(require_user_id)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> JSONResponse:
    user = await service.get_me(user_id)
    return Success.ok(data=user).to_resp()


@router.patch(
    path="/me",
    response_model=Success[UserSchema],
    summary="Self-service: update profile fields and/or rotate password",
)
async def update_me(
    payload: UserUpdateRequest,
    user_id: Annotated[uuid.UUID, Depends(require_user_id)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> JSONResponse:
    user = await service.update_me(
        user_id,
        full_name=payload.full_name,
        password=payload.password,
    )
    return Success.ok(data=user).to_resp()
