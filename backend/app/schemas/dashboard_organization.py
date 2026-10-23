"""Pydantic validation schemas for the organization role dashboard."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrganizationPostingsSummary(BaseModel):
    """Posting counts grouped by lifecycle status."""

    counts_by_status: dict[str, int]
    total: int


class OrganizationApplicationItem(BaseModel):
    """Recent applicant item for an organization's postings."""

    model_config = ConfigDict(from_attributes=True)

    application_id: int
    applicant_name: str
    applicant_email: str
    posting_id: int
    posting_title: str
    status: str
    applied_at: datetime


class OrganizationDashboardResponse(BaseModel):
    """Aggregated dashboard payload for organizations."""

    approval_status: str
    approval_note: str | None = None
    postings: OrganizationPostingsSummary
    posting_counts: dict[str, int] | None = None
    applications_awaiting_decision: int
    recent_applications: list[OrganizationApplicationItem]

    def model_post_init(self, __context: object) -> None:
        if self.posting_counts is None and self.postings:
            self.posting_counts = self.postings.counts_by_status
