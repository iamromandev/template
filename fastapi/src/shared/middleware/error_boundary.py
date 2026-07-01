"""Last-resort error boundary middleware.

Catches any exception that escapes all other handlers and middleware,
and returns a graceful JSON ``Error`` response (status 500) instead of
a raw 500 or traceback.

Must be mounted **innermost** (last-added in FastAPI, which means it
runs outermost in the Starlette chain) — see ``main.create_app()``.
"""

from __future__ import annotations

import traceback

from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.core.error import Error, ErrorDetail
from src.core.type import Code, ErrorType
from src.shared.middleware.request_id import get_request_id


class ErrorBoundaryMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except Exception as exc:
            tb_str = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
            request_id = get_request_id(request)
            logger.error(f"ErrorBoundary|request_id={request_id} unhandled:\n{tb_str}")

            error = Error(
                code=Code.INTERNAL_SERVER_ERROR,
                message="An unexpected error occurred.",
                error_type=ErrorType.SERVER_ERROR,
                details=[
                    ErrorDetail(
                        subject="server",
                        description=str(exc) if str(exc) else None,
                    )
                ],
            )
            return error.to_resp()
