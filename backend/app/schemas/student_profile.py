"""Pydantic schemas for student profile validation and response serialization."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    model_config = ConfigDict(extra="forbid")

    @field_validator("university", "department")
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
        """Trim bio and enforce maximum length of 1000 characters."""
        if value is None:
            return None
        trimmed = value.strip()
        if not trimmed:
            return None
        if len(trimmed) > 1000:
            raise ValueError("Bio cannot exceed 1000 characters.")
        return trimmed

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, value: list[str]) -> list[str]:
        """Validate, trim, deduplicate, and limit skills."""
        cleaned_skills: list[str] = []
        seen_lower: set[str] = set()

        for raw_skill in value:
            trimmed = raw_skill.strip()
            if not trimmed:
                continue
            if len(trimmed) > 40:
                raise ValueError("Each skill cannot exceed 40 characters.")
            lower = trimmed.lower()
            if lower not in seen_lower:
                seen_lower.add(lower)
                cleaned_skills.append(trimmed)

        if len(cleaned_skills) > 20:
            raise ValueError("At most 20 skills are permitted.")

        return cleaned_skills


class StudentProfileResponse(BaseModel):
    """Safe student profile response representation."""

    id: int
    user_id: int
    university: str | None = None
    department: str | None = None
    year_of_study: int | None = None
    bio: str | None = None
    skills: list[str] = Field(default_factory=list)
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, frozen=True)
