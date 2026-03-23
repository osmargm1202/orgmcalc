"""Common base schemas for pagination and shared models."""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict


class PaginationParams(BaseModel):
    """Query parameters for paginated lists."""

    offset: int = 0
    limit: int = 100


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    offset: int
    limit: int

    model_config = ConfigDict(arbitrary_types_allowed=True)


class FileAvailability(BaseModel):
    """File availability status for responses."""

    available: bool = False
    url: str | None = None


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


class ErrorResponse(BaseModel):
    """Error response structure."""

    detail: str
    code: str | None = None
