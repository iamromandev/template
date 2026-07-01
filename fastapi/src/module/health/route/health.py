from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.core.success import Success
from src.module.health.schema.response import HealthSchema
from src.module.health.service import get_health_service
from src.module.health.service.health_service import HealthService

router = APIRouter()


@router.get(
    path="/check",
    response_model=Success[HealthSchema],
)
async def check(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> JSONResponse:
    data = await health_service.check_health()
    return Success.ok(data=data).to_resp()
