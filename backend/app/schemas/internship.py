"""Validation schemas for internship postings."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.internship import InternshipStatus, InternshipWorkMode


class InternshipCreate(BaseModel):
    """Schema for creating a new internship posting."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=5000)
    requirements: str = Field(min_length=1, max_length=5000)
    location: str = Field(min_length=1, max_length=150)
    work_mode: InternshipWorkMode
    duration_weeks: int | None = Field(default=None, ge=1, le=104)
    application_deadline: datetime

    @field_validator("application_deadline")
    @classmethod
    def validate_future_deadline(cls, value: datetime) -> datetime:
        now = datetime.now(UTC)
        deadline = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
        if deadline <= now:
            raise ValueError("Application deadline must be set to a future date")
        return deadline


class InternshipUpdate(BaseModel):
    """Schema for updating an existing internship posting."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    requirements: str | None = Field(default=None, min_length=1, max_length=5000)
    location: str | None = Field(default=None, min_length=1, max_length=150)
    work_mode: InternshipWorkMode | None = None
    duration_weeks: int | None = Field(default=None, ge=1, le=104)
    application_deadline: datetime | None = None
    status: InternshipStatus | None = None

    @field_validator("application_deadline")
    @classmethod
    def validate_future_deadline_on_update(cls, value: datetime | None) -> datetime | None:
        if value is not None:
            now = datetime.now(UTC)
            deadline = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
            if deadline <= now:
                raise ValueError("Application deadline must be set to a future date")
            return deadline
        return value


class InternshipResponse(BaseModel):
    """Schema for returning internship posting details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    organization_name: str | None = None
    title: str
    description: str
    requirements: str
    location: str
    work_mode: InternshipWorkMode
    duration_weeks: int | None = None
    application_deadline: datetime
    status: InternshipStatus
    created_at: datetime
    updated_at: datetime
    applicant_count: int = 0
    applications_accepted: bool = True
    applied: bool | None = None
    application_status: str | None = None
    review_note: str | None = None
    reviewed_at: datetime | None = None
    reviewed_by: int | None = None


class InternshipListResponse(BaseModel):
    """Schema for paginated internship postings response."""

    items: list[InternshipResponse]
    total: int
    limit: int
    offset: int
