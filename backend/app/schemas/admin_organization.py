"""Pydantic schemas for admin organization approval management."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.organization_profile import ApprovalStatus


class AdminOrganizationApprovalRequest(BaseModel):
    """Schema for updating organization approval status and note."""

    approval_status: ApprovalStatus = Field(..., description="New approval status")
    approval_note: str | None = Field(
        default=None,
        max_length=500,
        description="Optional administrator review note",
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("approval_note")
    @classmethod
    def validate_approval_note(cls, value: str | None) -> str | None:
        """Validate approval note length and trim whitespace."""
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        if len(trimmed) > 500:
            raise ValueError("Approval note cannot exceed 500 characters.")
        return trimmed


class AdminOrganizationItem(BaseModel):
    """Item representation of an organization in admin directory."""

    user_id: int
    organization_name: str
    contact_name: str
    email: str
    industry: str | None = None
    location: str | None = None
    approval_status: ApprovalStatus
    approval_note: str | None = None
    reviewed_at: datetime | None = None
    reviewed_by: int | None = None

    model_config = ConfigDict(from_attributes=True, frozen=True)


class AdminOrganizationListResponse(BaseModel):
    """Paginated list of organizations for admin review."""

    items: list[AdminOrganizationItem]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(frozen=True)
