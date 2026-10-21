"""Domain service for aggregating organization dashboard metrics."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.user import User
from app.schemas.dashboard_organization import (
    OrganizationApplicationItem,
    OrganizationDashboardResponse,
    OrganizationPostingsSummary,
)


def get_organization_dashboard(db: Session, organization_id: int) -> OrganizationDashboardResponse:
    """Aggregate dashboard metrics for an authenticated organization account."""
    profile = db.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == organization_id)
    )
    approval_status = (
        profile.approval_status.value
        if profile and hasattr(profile.approval_status, "value")
        else (str(profile.approval_status) if profile else ApprovalStatus.PENDING.value)
    )
    approval_note = profile.approval_note if profile else None

    # Postings count by status
    postings_count_stmt = (
        select(Internship.status, func.count(Internship.id).label("count"))
        .where(Internship.organization_id == organization_id)
        .group_by(Internship.status)
    )
    posting_counts = {status.value: 0 for status in InternshipStatus}
    total_postings = 0
    for row in db.execute(postings_count_stmt).all():
        key = row.status.value if hasattr(row.status, "value") else str(row.status)
        posting_counts[key] = row.count
        total_postings += row.count

    # Applications awaiting decision (status == submitted)
    awaiting_stmt = (
        select(func.count(Application.id))
        .join(Internship, Application.posting_id == Internship.id)
        .where(
            Internship.organization_id == organization_id,
            Application.status == ApplicationStatus.SUBMITTED,
        )
    )
    awaiting_count = db.scalar(awaiting_stmt) or 0

    # 5 latest applications across its postings
    recent_apps_stmt = (
        select(
            Application.id.label("application_id"),
            User.full_name.label("applicant_name"),
            User.email.label("applicant_email"),
            Internship.id.label("posting_id"),
            Internship.title.label("posting_title"),
            Application.status.label("status"),
            Application.created_at.label("applied_at"),
        )
        .join(Internship, Application.posting_id == Internship.id)
        .join(User, Application.student_id == User.id)
        .where(Internship.organization_id == organization_id)
        .order_by(Application.created_at.desc(), Application.id.desc())
        .limit(5)
    )
    recent_rows = db.execute(recent_apps_stmt).all()
    recent_applications = [
        OrganizationApplicationItem(
            application_id=r.application_id,
            applicant_name=r.applicant_name,
            applicant_email=r.applicant_email,
            posting_id=r.posting_id,
            posting_title=r.posting_title,
            status=r.status.value if hasattr(r.status, "value") else str(r.status),
            applied_at=r.applied_at,
        )
        for r in recent_rows
    ]

    return OrganizationDashboardResponse(
        approval_status=approval_status,
        approval_note=approval_note,
        postings=OrganizationPostingsSummary(
            counts_by_status=posting_counts,
            total=total_postings,
        ),
        applications_awaiting_decision=awaiting_count,
        recent_applications=recent_applications,
    )
