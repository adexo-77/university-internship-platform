"""Pydantic schemas for organization profile validation and response serialization."""

from datetime import datetime
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
        """Enforce non-empty organization name."""
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Organization name cannot be blank.")
        if len(trimmed) > 255:
            raise ValueError("Organization name cannot exceed 255 characters.")
        return trimmed

    @field_validator("industry", "location")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        """Trim string and normalize empty to None."""
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        if len(trimmed) > 255:
            raise ValueError("Field cannot exceed 255 characters.")
        return trimmed

    @field_validator("website")
    @classmethod
    def validate_website(cls, value: str | None) -> str | None:
        """Ensure website is a valid http or https URL if provided."""
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        if len(trimmed) > 255:
            raise ValueError("Website URL cannot exceed 255 characters.")
        parsed = urlsplit(trimmed)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            raise ValueError("Website must be a valid http or https URL.")
        return trimmed

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        """Trim description and enforce maximum length of 1000 characters."""
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        if len(trimmed) > 1000:
            raise ValueError("Description cannot exceed 1000 characters.")
        return trimmed


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
