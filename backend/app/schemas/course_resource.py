"""Pydantic schemas for course resource management and discovery."""

from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.sanitization import clean_optional_text, clean_text


def _validate_url(v: str) -> str:
    """Validate that URL is non-empty, http/https, within length bounds, and safe."""
    if "\x00" in v:
        raise ValueError("URL cannot contain null bytes.")
    for ch in v:
        if ord(ch) < 32 or ord(ch) == 127:
            raise ValueError("URL cannot contain control characters.")
    stripped = v.strip()
    if not stripped:
        raise ValueError("URL cannot be empty.")
    if len(stripped) > 500:
        raise ValueError("URL cannot exceed 500 characters.")
    lowered = stripped.lower()
    if lowered.startswith("javascript:") or lowered.startswith("data:"):
        raise ValueError("URL scheme not allowed.")
    parsed = urlsplit(stripped)
    if parsed.scheme.lower() not in ("http", "https") or not parsed.netloc:
        raise ValueError("URL must be a valid http or https URL.")
    return stripped


class CourseResourceCreate(BaseModel):
    """Payload to add a course learning resource."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=120)
    url: str = Field(..., max_length=500)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        cleaned = clean_text(v, field_name="Title", max_length=120, allow_newlines=False)
        if not cleaned:
            raise ValueError("Title cannot be empty.")
        return cleaned

    @field_validator("url")
    @classmethod
    def validate_url_field(cls, v: str) -> str:
        return _validate_url(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        return clean_optional_text(v, field_name="Description", max_length=500, allow_newlines=True)


class CourseResourceUpdate(BaseModel):
    """Payload to update an existing course resource."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=120)
    url: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str | None) -> str | None:
        if v is None:
            return None
        cleaned = clean_text(v, field_name="Title", max_length=120, allow_newlines=False)
        if not cleaned:
            raise ValueError("Title cannot be empty.")
        return cleaned

    @field_validator("url")
    @classmethod
    def validate_url_field(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return _validate_url(v)

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return clean_optional_text(v, field_name="Description", max_length=500, allow_newlines=True)


class CourseResourceResponse(BaseModel):
    """Representation of a course learning resource."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    title: str
    url: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime
