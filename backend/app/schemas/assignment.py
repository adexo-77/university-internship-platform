"""Pydantic validation schemas for course assignments."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssignmentCreate(BaseModel):
    """Payload to create a new assignment."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    due_at: datetime
    max_points: int = Field(default=100, ge=1, le=1000)

    @field_validator("due_at")
    @classmethod
    def validate_due_at_in_future(cls, value: datetime) -> datetime:
        """Ensure due_at is timezone-aware and set in the future."""
        if value.tzinfo is None:
            value = value.replace(tzinfo=UTC)
        now = datetime.now(UTC)
        if value <= now:
            raise ValueError("Due date must be in the future")
        return value


class AssignmentUpdate(BaseModel):
    """Payload to update an existing assignment."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    due_at: datetime | None = None
    max_points: int | None = Field(default=None, ge=1, le=1000)

    @field_validator("due_at")
    @classmethod
    def ensure_timezone(cls, value: datetime | None) -> datetime | None:
        """Ensure due_at has a timezone if provided."""
        if value is not None and value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class AssignmentResponse(BaseModel):
    """Serialized assignment representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    title: str
    description: str | None = None
    due_at: datetime
    max_points: int
    created_at: datetime
    updated_at: datetime
    submission_status: str | None = None
    is_late: bool | None = None
    grade: int | None = None
    course_title: str | None = None
