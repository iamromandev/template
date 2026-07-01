from src.core.base import BaseService
from src.core.common import get_app_version
from src.core.type import Status
from src.data.db import get_db_health, get_db_version
from src.data.db.repo.health_check_log_repo import HealthCheckLogRepo
from src.module.health.schema.response import DatabaseSchema, HealthSchema


class HealthService(BaseService):
    """Health check business logic.

    Each health check is persisted to HealthCheckLog so the system
    maintains an audit trail of uptime history.
    """

    def __init__(self, repo: HealthCheckLogRepo) -> None:
        self._repo = repo

    async def check_health(self) -> HealthSchema:
        db_status = Status.SUCCESS if await get_db_health() else Status.ERROR
        db_version = await get_db_version()

        # Persist the health check for audit trail
        await self._repo.create(
            status=db_status.value,
            db_version=db_version,
        )

        return HealthSchema(
            version=get_app_version(),
            db=DatabaseSchema(status=db_status, version=db_version),
        )
