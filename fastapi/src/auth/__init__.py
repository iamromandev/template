"""Authentication & authorization infra.

This is the **shared** auth layer — modules don't define JWT / OAuth2
themselves, they depend on the FastAPI dependencies in ``src.deps.auth``.
"""

from src.auth.jwt import JWTIssuer as JWTIssuer
from src.auth.jwt import jwt_issuer as jwt_issuer
from src.auth.oauth2 import oauth2_scheme as oauth2_scheme
from src.auth.permission import Permission as Permission
from src.auth.permission import Role as Role
from src.auth.permission import require_permission as require_permission
from src.auth.permission import require_role as require_role
