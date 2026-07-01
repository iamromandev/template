"""Health module request schemas.

This module is kept for structural consistency — other modules will
have CreateRequest, UpdateRequest, ListParams, etc. here.

For the health check endpoint no request body is required (GET).
"""

from typing import Annotated

from pydantic import BaseModel, Field


class HealthLogListParams(BaseModel):
    """Query parameters for listing health check logs."""

    limit: Annotated[int, Field(default=10, ge=1, le=100)]
    offset: Annotated[int, Field(default=0, ge=0)]
