from src.data.db.repo.user_repo import UserRepo
from src.module.user.service.user_service import UserService


def get_user_service() -> UserService:
    """DI factory for ``UserService``.

    Mirrors the pattern used by ``src.module.health.service.get_health_service``:
    instantiate the repo here and inject it. Module-local by design —
    tests override via FastAPI's ``app.dependency_overrides``.
    """
    return UserService(repo=UserRepo())


__all__ = ["UserService", "get_user_service"]
