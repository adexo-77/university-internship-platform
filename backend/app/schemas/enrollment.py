"""Pydantic schemas for course enrollments and rosters."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EnrolledStudentResponse(BaseModel):
    """Roster item representing an enrolled student."""

    model_config = ConfigDict(from_attributes=True)

    student_id: int
    name: str
    email: str
    enrolled_at: datetime


class EnrollmentResponse(BaseModel):
    """Response returned upon successful course enrollment."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    student_id: int
    enrolled_at: datetime
    message: str = "Enrolled successfully"


class EnrollmentActionResponse(BaseModel):
    """Standard message response for enrollment actions such as leaving a course."""

    detail: str
