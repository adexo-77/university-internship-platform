"""Pydantic validation schemas for the admin role dashboard."""

from pydantic import BaseModel


class AdminDashboardResponse(BaseModel):
    """Aggregated platform health and activity metrics for administrators."""

    users_by_role: dict[str, int]
    users_active_count: int
    active_users_count: int | None = None
    users_total_count: int
    organizations_pending_approval: int
    postings_pending_review: int
    internships_pending_review: int | None = None
    open_internships: int
    courses_by_status: dict[str, int]
    applications_by_status: dict[str, int]

    def model_post_init(self, __context: object) -> None:
        if self.active_users_count is None:
            self.active_users_count = self.users_active_count
        if self.internships_pending_review is None:
            self.internships_pending_review = self.postings_pending_review
