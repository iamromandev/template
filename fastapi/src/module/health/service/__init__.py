from src.data.db.repo.health_check_log_repo import HealthCheckLogRepo
from src.module.health.service.health_service import HealthService


def get_health_service() -> HealthService:
    """DI factory for HealthService.

    In production this is typically wired via a container (see src/deps/).
    For the template we keep it simple: instantiate the repo and pass it in.
    """
    return HealthService(repo=HealthCheckLogRepo())
