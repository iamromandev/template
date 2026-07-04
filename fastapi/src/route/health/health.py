from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.core.success import Success
from src.data.db.schema import HealthSchema
from src.service.health import HealthService, get_health_service

router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    path="/check",
    response_model=Success[HealthSchema],
)
async def check(
        health_service: Annotated[HealthService, Depends(get_health_service)],
) -> JSONResponse:
    data = await health_service.check_health()
    return Success.ok(data=data).to_resp()
