"""Pydantic schemas for admin user management."""

import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user import UserRole


class AdminCreatableRole(enum.StrEnum):
    """Roles permitted to be provisioned via admin user creation."""

    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    COORDINATOR = "coordinator"


class AdminUserCreateRequest(BaseModel):
    """Schema for admin provisioning of instructor, admin, or coordinator accounts."""

    full_name: str = Field(..., min_length=1, max_length=255, description="Full name of user")
    email: str = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password between 8 and 128 characters",
    )
    role: AdminCreatableRole = Field(
        ..., description="Account role: must be 'instructor', 'admin', or 'coordinator'"
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("email")
    @classmethod
    def validate_and_normalize_email(cls, value: str) -> str:
        """Validate and lowercase email address."""
        normalized = value.strip().lower()
        if not normalized or "@" not in normalized or "." not in normalized.split("@")[-1]:
            raise ValueError("A valid email address is required.")
        return normalized

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        """Validate full name is not blank."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Full name cannot be blank.")
        return cleaned


class AdminUserUpdateRequest(BaseModel):
    """Schema for updating user active status."""

    is_active: bool = Field(..., description="Target active state for user account")

    model_config = ConfigDict(extra="forbid")


class AdminUserPasswordResetRequest(BaseModel):
    """Schema for admin resetting a user password."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New password between 8 and 128 characters",
    )

    model_config = ConfigDict(extra="forbid")


class AdminUserResponse(BaseModel):
    """User account response safe representation (excludes password hash)."""

    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, frozen=True)


class AdminUserListResponse(BaseModel):
    """Paginated list of users for admin directory."""

    items: list[AdminUserResponse]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(frozen=True)
