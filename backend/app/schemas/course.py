"""Pydantic schemas for course management and discovery."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.course import CourseStatus


class CourseCreate(BaseModel):
    """Payload to create a new course."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    status: CourseStatus = Field(default=CourseStatus.DRAFT)


class CourseUpdate(BaseModel):
    """Payload to update an existing course."""

    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    status: CourseStatus | None = Field(default=None)


class CourseResponse(BaseModel):
    """Course item representation returned by endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    instructor_id: int
    instructor_name: str | None = None
    title: str
    description: str | None = None
    status: CourseStatus
    created_at: datetime
    updated_at: datetime
    enrolled: bool | None = None
    enrolled_count: int | None = None


class CourseListResponse(BaseModel):
    """Paginated list of courses with total count."""

    model_config = ConfigDict(from_attributes=True)

    items: list[CourseResponse]
    total: int
    limit: int
    offset: int
