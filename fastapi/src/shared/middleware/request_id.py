"""Request-ID middleware.

* If the inbound request carries ``X-Request-ID``, reuse it (so traces
  propagate across services).
* Otherwise generate a fresh UUID4.
* Stash the id on ``request.state.request_id`` and reflect it on the
  response as ``X-Request-ID``.
"""

from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore[override]
        incoming = request.headers.get(REQUEST_ID_HEADER)
        request_id = incoming if incoming else uuid.uuid4().hex
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def get_request_id(request: Request) -> str:
    """Convenience accessor used by other middleware / handlers."""
    return getattr(request.state, "request_id", "-")
