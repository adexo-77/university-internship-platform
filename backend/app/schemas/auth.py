"""Pydantic schemas for authentication and user accounts."""

import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

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
        """Validate full name is not just whitespace."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Full name cannot be blank.")
        return cleaned


class LoginRequest(BaseModel):
    """Schema for user credentials login."""

    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="Account password")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        """Normalize email address to lowercase."""
        return value.strip().lower()


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
