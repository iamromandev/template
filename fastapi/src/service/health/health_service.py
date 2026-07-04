from src.core.base import BaseService
from src.core.common import get_app_version
from src.core.type import Status
from src.data.db import get_db_health, get_db_version
from src.data.db.schema import DatabaseSchema, HealthSchema


class HealthService(BaseService):
    """Health check business logic."""

    async def check_health(self) -> HealthSchema:
        db_status = Status.SUCCESS if await get_db_health() else Status.ERROR
        db_version = await get_db_version()

        return HealthSchema(
            version=get_app_version(),
            db=DatabaseSchema(status=db_status, version=db_version),
        )
