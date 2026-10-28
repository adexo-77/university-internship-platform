"""Validation and serialization schemas for suggested internships."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.internship import InternshipStatus, InternshipWorkMode


class InternshipSuggestionReasons(BaseModel):
    """Detailed matching criteria reasons for a suggested internship."""

    matched_skills: list[str] = Field(default_factory=list)
    work_mode_match: bool | None = None
    location_match: bool | None = None

    model_config = ConfigDict(frozen=True)


class InternshipSuggestionItem(BaseModel):
    """Suggested internship posting with match score and reasons."""

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
    applied: bool | None = False
    application_status: str | None = None
    review_note: str | None = None
    reviewed_at: datetime | None = None
    reviewed_by: int | None = None
    score: int = Field(ge=0, le=100)
    reasons: InternshipSuggestionReasons

    model_config = ConfigDict(from_attributes=True, frozen=True)


class InternshipSuggestionResponse(BaseModel):
    """Response containing list of suggested internships and optional reason code."""

    items: list[InternshipSuggestionItem] = Field(default_factory=list)
    reason_code: str | None = None

    model_config = ConfigDict(from_attributes=True, frozen=True)
