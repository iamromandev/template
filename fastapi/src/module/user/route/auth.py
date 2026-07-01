"""Authentication routes — register / login / refresh / logout.

These live under ``/users/auth`` (because they share the user module),
but the OAuth2 ``tokenUrl`` advertised in the OpenAPI spec points at
``/api/v1/users/auth/login`` via the override in main.py.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.core.success import Success
from src.module.user.schema.request import LoginRequest, RefreshRequest, RegisterRequest
from src.module.user.schema.response import TokenSchema, UserSchema
from src.module.user.service import UserService, get_user_service
from src.shared.deps.auth import require_user_id

router = APIRouter()


@router.post(
    path="/auth/register",
    response_model=Success[UserSchema],
    status_code=201,
    summary="Register a new account",
)
async def register(
    payload: RegisterRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> JSONResponse:
    user = await service.register(
        email=payload.email,
        username=payload.username,
        password=payload.password,
        full_name=payload.full_name,
    )
    return Success.created(data=user).to_resp()


@router.post(
    path="/auth/login",
    response_model=Success[TokenSchema],
    summary="OAuth2 password flow — exchange username/email + password for tokens",
)
async def login(
    payload: LoginRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> JSONResponse:
    token = await service.authenticate(
        identifier=payload.username,
        password=payload.password,
    )
    return Success.ok(data=token).to_resp()


@router.post(
    path="/auth/refresh",
    response_model=Success[TokenSchema],
    summary="Rotate access + refresh tokens using a valid refresh token",
)
async def refresh(
    payload: RefreshRequest,
    service: Annotated[UserService, Depends(get_user_service)],
) -> JSONResponse:
    token = await service.refresh(refresh_token=payload.refresh_token)
    return Success.ok(data=token).to_resp()


@router.get(
    path="/auth/me",
    response_model=Success[UserSchema],
    summary="Get the current authenticated user",
)
async def me(
    user_id: Annotated[uuid.UUID, Depends(require_user_id)],
    service: Annotated[UserService, Depends(get_user_service)],
) -> JSONResponse:
    user = await service.get_me(user_id)
    return Success.ok(data=user).to_resp()
