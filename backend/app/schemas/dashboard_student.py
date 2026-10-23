"""Pydantic validation schemas for the student role dashboard."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StudentDueNextItem(BaseModel):
    """Upcoming unsubmitted assignment in an enrolled published course."""

    model_config = ConfigDict(from_attributes=True)

    assignment_id: int
    title: str
    course_id: int
    course_title: str
    due_at: datetime


class StudentRecentGradeItem(BaseModel):
    """Recently graded assignment submission for the student."""

    model_config = ConfigDict(from_attributes=True)

    submission_id: int
    assignment_id: int
    assignment_title: str
    course_title: str
    grade: int
    max_points: int
    graded_at: datetime | None = None


class StudentCourseProgressItem(BaseModel):
    """Course completion and academic grade performance progress."""

    model_config = ConfigDict(from_attributes=True)

    course_id: int
    title: str
    instructor_name: str | None = None
    assignments_total: int
    assignments_submitted: int
    progress_percent: float
    average_grade_percent: float | None = None


class StudentApplicationRecentItem(BaseModel):
    """Recent internship application item."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    posting_id: int
    posting_title: str
    organization_name: str
    status: str
    applied_at: datetime


class StudentApplicationsSummary(BaseModel):
    """Aggregated status counts and latest applications."""

    counts_by_status: dict[str, int]
    recent: list[StudentApplicationRecentItem]


class StudentDashboardResponse(BaseModel):
    """Aggregated dashboard payload for students."""

    due_next: list[StudentDueNextItem]
    recent_grades: list[StudentRecentGradeItem]
    courses: list[StudentCourseProgressItem]
    applications: StudentApplicationsSummary
    profile_complete: bool
