"""Pydantic schemas for student rule-based study plan and weekly progress summary."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class StudyPlanItem(BaseModel):
    """An actionable study or application task in the study plan."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    type: str  # "assignment" | "internship"
    title: str
    course_title: str | None = None
    link_path: str
    due_at: datetime
    suggested_minutes: int
    reason: str
    flags: list[str] = Field(default_factory=list)


class StudyPlanDay(BaseModel):
    """Plan items allocated to a specific calendar date in the study window."""

    date: date
    items: list[StudyPlanItem] = Field(default_factory=list)
    total_minutes: int = 0


class StudyPlanWindow(BaseModel):
    """Temporal boundaries of the generated study plan."""

    start_date: date
    end_date: date
    days: int


class StudyPlanMetrics(BaseModel):
    """Key metric counts summarizing current student commitments."""

    enrolled_courses_count: int
    assignments_due_count: int
    overdue_count: int
    tight_count: int
    total_suggested_minutes: int
    applications_count: int
    open_internships_count: int


class StudyPlanSummary(BaseModel):
    """Synthesized text summary and headline derived deterministically from student data."""

    headline: str
    sentences: list[str]
    metrics: StudyPlanMetrics


class StudyPlanResponse(BaseModel):
    """Complete rule-based study plan and weekly progress summary payload."""

    generated_at: datetime
    window: StudyPlanWindow
    summary: StudyPlanSummary
    plan: list[StudyPlanDay]
    overdue: list[StudyPlanItem] = Field(default_factory=list)
    tight: list[StudyPlanItem] = Field(default_factory=list)
    rules: list[str]
