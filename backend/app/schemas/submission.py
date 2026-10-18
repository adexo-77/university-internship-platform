"""Pydantic validation schemas for assignment submissions and grading."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SubmissionSubmit(BaseModel):
    """Payload for submitting or resubmitting assignment work."""

    model_config = ConfigDict(extra="forbid")

    content: str = Field(..., min_length=1, max_length=10000)
    link_url: str | None = Field(default=None, max_length=2048)

    @field_validator("link_url")
    @classmethod
    def validate_link_url_scheme(cls, value: str | None) -> str | None:
        """Ensure link_url starts with http:// or https://."""
        if value is None or not value.strip():
            return None
        stripped = value.strip()
        if not (stripped.startswith("http://") or stripped.startswith("https://")):
            raise ValueError("link_url must start with http:// or https://")
        return stripped


class SubmissionGrade(BaseModel):
    """Payload for grading an assignment submission."""

    model_config = ConfigDict(extra="forbid")

    grade: int = Field(..., ge=0)
    feedback: str | None = Field(default=None, max_length=2000)


class SubmissionResponse(BaseModel):
    """Serialized submission model."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    assignment_id: int
    student_id: int
    content: str
    link_url: str | None = None
    is_late: bool
    submitted_at: datetime
    updated_at: datetime
    grade: int | None = None
    feedback: str | None = None
    graded_at: datetime | None = None
    graded_by: int | None = None


class StudentSubmissionRosterItem(BaseModel):
    """Enrolled student with their submission record if present."""

    model_config = ConfigDict(from_attributes=True)

    student_id: int
    student_name: str
    student_email: str
    submission: SubmissionResponse | None = None
