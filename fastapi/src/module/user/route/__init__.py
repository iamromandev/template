"""User module — HTTP routes.

Two sub-routers:
    * ``auth``  — register / login / refresh  (mounted at ``/auth``)
    * ``users`` — /me + admin CRUD            (mounted at ``/users``)

Both are aggregated under a single module router at ``/users``.
"""

from fastapi import APIRouter

from src.module.user.route.auth import router as _auth_router
from src.module.user.route.user import router as _user_router

_subrouters = [_auth_router, _user_router]

router = APIRouter(prefix="/users", tags=["Users"])

for subrouter in _subrouters:
    router.include_router(subrouter)
