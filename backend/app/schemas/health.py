"""Health check response schemas."""

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    """Schema for root health status."""

    status: str
    public_demo: bool = False

    model_config = ConfigDict(frozen=True)


class DatabaseHealthResponse(BaseModel):
    """Schema for database health status."""

    database: str

    model_config = ConfigDict(frozen=True)


class ErrorDetailResponse(BaseModel):
    """Consistent API error format."""

    detail: str
    code: str | None = None

    model_config = ConfigDict(frozen=True)
