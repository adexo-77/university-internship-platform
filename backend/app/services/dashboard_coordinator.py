"""Domain service for aggregating coordinator dashboard metrics."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.schemas.dashboard_coordinator import CoordinatorDashboardResponse


def get_coordinator_dashboard(db: Session, coordinator_id: int) -> CoordinatorDashboardResponse:
    """Aggregate review queues, open postings, application statuses, and completed reviews."""
    orgs_pending = (
        db.scalar(
            select(func.count(OrganizationProfile.id)).where(
                OrganizationProfile.approval_status == ApprovalStatus.PENDING
            )
        )
        or 0
    )

    internships_pending = (
        db.scalar(
            select(func.count(Internship.id)).where(
                Internship.status == InternshipStatus.PENDING_REVIEW
            )
        )
        or 0
    )

    open_internships_count = (
        db.scalar(
            select(func.count(Internship.id)).where(Internship.status == InternshipStatus.OPEN)
        )
        or 0
    )

    apps_stmt = select(Application.status, func.count(Application.id).label("count")).group_by(
        Application.status
    )
    apps_by_status = {status.value: 0 for status in ApplicationStatus}
    for row in db.execute(apps_stmt).all():
        key = row.status.value if hasattr(row.status, "value") else str(row.status)
        apps_by_status[key] = row.count

    org_reviews = (
        db.scalar(
            select(func.count(OrganizationProfile.id)).where(
                OrganizationProfile.reviewed_by == coordinator_id
            )
        )
        or 0
    )
    internship_reviews = (
        db.scalar(select(func.count(Internship.id)).where(Internship.reviewed_by == coordinator_id))
        or 0
    )
    reviews_completed = org_reviews + internship_reviews

    return CoordinatorDashboardResponse(
        organizations_pending_approval=orgs_pending,
        internships_pending_review=internships_pending,
        open_internships=open_internships_count,
        applications_by_status=apps_by_status,
        reviews_completed=reviews_completed,
    )
