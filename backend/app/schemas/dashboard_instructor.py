"""Pydantic validation schemas for the instructor role dashboard."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InstructorCourseItem(BaseModel):
    """Summary of an instructor-owned course with engagement metrics."""

    model_config = ConfigDict(from_attributes=True)

    course_id: int
    title: str
    status: str
    enrolled_count: int
    assignments_count: int
    submissions_awaiting_grading: int
    awaiting_grading_count: int | None = None
    average_grade_percent: float | None = None

    def model_post_init(self, __context: object) -> None:
        if self.awaiting_grading_count is None:
            self.awaiting_grading_count = self.submissions_awaiting_grading


class InstructorNeedsGradingItem(BaseModel):
    """Pending ungraded student submission awaiting review."""

    model_config = ConfigDict(from_attributes=True)

    submission_id: int
    student_name: str
    assignment_id: int
    assignment_title: str
    course_id: int
    course_title: str
    submitted_at: datetime
    late: bool
    is_late: bool | None = None

    def model_post_init(self, __context: object) -> None:
        if self.is_late is None:
            self.is_late = self.late


class InstructorDashboardResponse(BaseModel):
    """Aggregated dashboard payload for instructors."""

    courses: list[InstructorCourseItem]
    needs_grading: list[InstructorNeedsGradingItem]
