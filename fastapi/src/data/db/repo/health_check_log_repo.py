from src.core.base import BaseRepo
from src.data.db.model.health_check_log import HealthCheckLog


class HealthCheckLogRepo(BaseRepo[HealthCheckLog]):
    def __init__(self) -> None:
        super().__init__(HealthCheckLog)

    async def get_recent(self, limit: int = 10) -> list[HealthCheckLog]:
        return await self.get_many(order_by="-created_at", limit=limit)
