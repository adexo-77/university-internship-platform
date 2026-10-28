"""Pydantic schemas for student profile validation and response serialization."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.sanitization import clean_optional_text, clean_text


class StudentProfileUpdateRequest(BaseModel):
    """Schema for updating student profile details."""

    university: str | None = Field(
        default=None,
        description="University or educational institution name",
    )
    department: str | None = Field(
        default=None,
        description="Academic department or field of study",
    )
    year_of_study: int | None = Field(
        default=None,
        description="Current academic year between 1 and 6",
    )
    bio: str | None = Field(
        default=None,
        description="Personal biography and academic interests (max 1000 characters)",
    )
    skills: list[str] = Field(
        default_factory=list,
        description="List of skills (at most 20 skills, up to 40 characters each)",
    )
    preferred_work_modes: list[str] = Field(
        default_factory=list,
        description="Preferred internship work modes (onsite, remote, hybrid)",
    )
    preferred_location: str | None = Field(
        default=None,
        description="Preferred work location (up to 80 characters)",
    )

    model_config = ConfigDict(extra="forbid")

    @field_validator("university", "department")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        """Trim string, reject null bytes/control chars, and normalize empty to None."""
        return clean_optional_text(value, max_length=255, allow_newlines=False)

    @field_validator("year_of_study")
    @classmethod
    def validate_year_of_study(cls, value: int | None) -> int | None:
        """Ensure year of study is between 1 and 6 if specified."""
        if value is None:
            return None
        if value < 1 or value > 6:
            raise ValueError("Year of study must be between 1 and 6.")
        return value

    @field_validator("bio")
    @classmethod
    def validate_bio(cls, value: str | None) -> str | None:
        """Trim bio, reject null bytes, and enforce maximum length of 1000 characters."""
        return clean_optional_text(value, field_name="Bio", max_length=1000, allow_newlines=True)

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, value: list[str]) -> list[str]:
        """Validate, trim, deduplicate, and limit skills."""
        cleaned_skills: list[str] = []
        seen_lower: set[str] = set()

        for raw_skill in value:
            trimmed = clean_text(raw_skill, field_name="Skill", max_length=40, allow_newlines=False)
            if not trimmed:
                continue
            lower = trimmed.lower()
            if lower not in seen_lower:
                seen_lower.add(lower)
                cleaned_skills.append(trimmed)

        if len(cleaned_skills) > 20:
            raise ValueError("At most 20 skills are permitted.")

        return cleaned_skills

    @field_validator("preferred_work_modes")
    @classmethod
    def validate_preferred_work_modes(cls, value: list[str]) -> list[str]:
        """Validate, trim, deduplicate, and enforce allowed work modes."""
        cleaned_modes: list[str] = []
        seen: set[str] = set()
        allowed = {"onsite", "remote", "hybrid"}

        for raw_mode in value:
            trimmed = clean_text(
                raw_mode, field_name="Work mode", max_length=20, allow_newlines=False
            ).lower()
            if trimmed not in allowed:
                raise ValueError(
                    f"Invalid work mode: {trimmed}. Allowed modes are onsite, remote, hybrid."
                )
            if trimmed not in seen:
                seen.add(trimmed)
                cleaned_modes.append(trimmed)

        return cleaned_modes

    @field_validator("preferred_location")
    @classmethod
    def validate_preferred_location(cls, value: str | None) -> str | None:
        """Sanitize preferred location, enforcing max length 80 and no control characters."""
        return clean_optional_text(
            value, field_name="Preferred location", max_length=80, allow_newlines=False
        )


class StudentProfileResponse(BaseModel):
    """Safe student profile response representation."""

    id: int
    user_id: int
    university: str | None = None
    department: str | None = None
    year_of_study: int | None = None
    bio: str | None = None
    skills: list[str] = Field(default_factory=list)
    preferred_work_modes: list[str] = Field(default_factory=list)
    preferred_location: str | None = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, frozen=True)
