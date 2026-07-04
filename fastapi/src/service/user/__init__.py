from collections.abc import AsyncGenerator

from src.data.db.repo.user_repo import UserRepo
from src.service.user.user_service import UserService


async def get_user_service() -> AsyncGenerator[UserService]:
    yield UserService(repo=UserRepo())
