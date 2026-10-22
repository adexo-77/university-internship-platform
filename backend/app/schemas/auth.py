"""Pydantic schemas for authentication and user accounts."""

import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.core.sanitization import clean_optional_text, clean_text, normalize_email
from app.models.user import UserRole


class PublicRegisterRole(enum.StrEnum):
    """Permitted roles for public registration."""

    STUDENT = "student"
    ORGANIZATION = "organization"


class RegisterRequest(BaseModel):
    """Schema for public user registration."""

    email: str = Field(..., description="User email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User password between 8 and 128 characters",
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Full name of the user or organization representative",
    )
    role: PublicRegisterRole = Field(
        ...,
        description="Account role: must be 'student' or 'organization'",
    )
    organization_name: str | None = Field(
        default=None,
        description="Required when registering as an organization",
    )

    @field_validator("email")
    @classmethod
    def validate_and_normalize_email(cls, value: str) -> str:
        """Validate and safely normalize email address."""
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Reject null bytes and control chars in password."""
        return clean_text(value, "Password", max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        """Validate full name is not just whitespace and contains no null bytes."""
        cleaned = clean_text(value, "Full name", max_length=255)
        if not cleaned:
            raise ValueError("Full name cannot be blank.")
        return cleaned

    @field_validator("organization_name")
    @classmethod
    def validate_organization_name(cls, value: str | None) -> str | None:
        """Trim and sanitize organization_name if provided."""
        return clean_optional_text(value, "Organization name", max_length=255)

    @model_validator(mode="after")
    def validate_organization_role(self) -> "RegisterRequest":
        """Validate that organization registration includes organization_name."""
        if self.role == PublicRegisterRole.ORGANIZATION:
            if not self.organization_name:
                raise ValueError("Organization name is required for organization registration.")
            if len(self.organization_name) > 255:
                raise ValueError("Organization name cannot exceed 255 characters.")
        return self


class LoginRequest(BaseModel):
    """Schema for user credentials login."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="Account password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Safely normalize email address."""
        return normalize_email(value)

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Reject null bytes and control chars in password."""
        return clean_text(value, "Password", max_length=128)


class UserResponse(BaseModel):
    """Safe user profile response schema (excludes password_hash and tokens)."""

    id: int
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, frozen=True)


class ChangePasswordRequest(BaseModel):
    """Schema for authenticated password change."""

    current_password: str = Field(..., min_length=1, description="Current account password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="New account password between 8 and 128 characters",
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("current_password")
    @classmethod
    def validate_current_password(cls, value: str) -> str:
        """Reject null bytes and control chars in current password."""
        return clean_text(value, "Current password", max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        """Reject null bytes and control chars in new password."""
        return clean_text(value, "New password", max_length=128)

    @model_validator(mode="after")
    def validate_new_differs_from_current(self) -> "ChangePasswordRequest":
        """Enforce new password is different from current password."""
        if self.current_password == self.new_password:
            raise ValueError("New password must be different from current password.")
        return self
