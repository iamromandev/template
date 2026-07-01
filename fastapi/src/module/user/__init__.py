"""User module — second domain module.

Demonstrates the same self-contained pattern as ``health``, with auth
flavoured additions:
    * hashed password storage (bcrypt)
    * role enum (USER / ADMIN / SUPERADMIN)
    * email uniqueness
"""

from src.module.user.route import router as user_router

__all__ = ["user_router"]
