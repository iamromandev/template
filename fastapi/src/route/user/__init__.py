from fastapi import APIRouter

from src.route.user.auth import router as _auth_router
from src.route.user.user import router as _user_router

_subrouters = [_auth_router, _user_router]

router = APIRouter(prefix="/users", tags=["Users"])

for subrouter in _subrouters:
    router.include_router(subrouter)

__all__ = ["router"]
