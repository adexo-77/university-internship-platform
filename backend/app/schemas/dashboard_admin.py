"""Pydantic validation schemas for the admin role dashboard."""

from pydantic import BaseModel


class AdminDashboardResponse(BaseModel):
    """Aggregated platform health and activity metrics for administrators."""

    users_by_role: dict[str, int]
    users_active_count: int
    users_total_count: int
    organizations_pending_approval: int
    postings_pending_review: int
    open_internships: int
    courses_by_status: dict[str, int]
    applications_by_status: dict[str, int]
