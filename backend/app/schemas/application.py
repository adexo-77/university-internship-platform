"""Validation schemas for internship applications and decisions."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.application import ApplicationStatus


class ApplicationCreate(BaseModel):
    """Schema for submitting an application to an internship posting."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    cover_letter: str = Field(min_length=1, max_length=5000)


class ApplicationDecision(BaseModel):
    """Schema for recording an organization's decision on an application."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    status: ApplicationStatus = Field(
        description="Allowed decision statuses: shortlisted, accepted, rejected"
    )
    decision_message: str | None = Field(default=None, max_length=1000)


class ApplicantProfile(BaseModel):
    """Snapshot of applicant student profile for organization/admin review."""

    model_config = ConfigDict(from_attributes=True)

    user_id: int
    full_name: str
    email: str
    university: str | None = None
    department: str | None = None
    year_of_study: int | None = None
    skills: list[str] = []
    bio: str | None = None


class ApplicationResponse(BaseModel):
    """Schema for returning application data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    posting_id: int
    posting_title: str | None = None
    organization_name: str | None = None
    student_id: int
    cover_letter: str
    status: ApplicationStatus
    decision_message: str | None = None
    decided_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    applicant: ApplicantProfile | None = None
