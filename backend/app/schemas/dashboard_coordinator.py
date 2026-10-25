"""Pydantic validation schemas for the coordinator role dashboard."""

from pydantic import BaseModel


class CoordinatorDashboardResponse(BaseModel):
    """Aggregated platform workflow metrics for internship coordinators."""

    organizations_pending_approval: int
    internships_pending_review: int
    open_internships: int
    applications_by_status: dict[str, int]
    reviews_completed: int
