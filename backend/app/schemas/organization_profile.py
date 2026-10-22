"""Pydantic schemas for organization profile validation and response serialization."""

from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.sanitization import clean_optional_text, clean_text
from app.models.organization_profile import ApprovalStatus


class OrganizationProfileUpdateRequest(BaseModel):
    """Schema for updating organization profile details."""

    organization_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the organization",
    )
    industry: str | None = Field(
        default=None,
        description="Industry sector or domain",
    )
    location: str | None = Field(
        default=None,
        description="Physical headquarters or office location",
    )
    website: str | None = Field(
        default=None,
        description="Valid HTTP or HTTPS website URL",
    )
    description: str | None = Field(
        default=None,
        description="Organization overview and mission (max 1000 characters)",
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("organization_name")
    @classmethod
    def validate_organization_name(cls, value: str) -> str:
        """Enforce non-empty organization name without null bytes."""
        cleaned = clean_text(value, "Organization name", max_length=255)
        if not cleaned:
            raise ValueError("Organization name cannot be blank.")
        return cleaned

    @field_validator("industry", "location")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        """Trim string, reject null bytes, and normalize empty to None."""
        return clean_optional_text(value, max_length=255, allow_newlines=False)

    @field_validator("website")
    @classmethod
    def validate_website(cls, value: str | None) -> str | None:
        """Ensure website is a valid http or https URL if provided."""
        cleaned = clean_optional_text(value, "Website", max_length=255)
        if cleaned is None:
            return None
        parsed = urlsplit(cleaned)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Website must be a valid http or https URL.")
        return cleaned

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        """Trim description and enforce maximum length of 1000 characters."""
        return clean_optional_text(
            value, field_name="Description", max_length=1000, allow_newlines=True
        )


class OrganizationProfileResponse(BaseModel):
    """Safe organization profile response representation."""

    id: int
    user_id: int
    organization_name: str
    industry: str | None = None
    location: str | None = None
    website: str | None = None
    description: str | None = None
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    approval_note: str | None = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, frozen=True)
