"""Business logic for administrative internship review and management."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.application import Application
from app.models.internship import Internship, InternshipStatus
from app.models.organization_profile import OrganizationProfile
from app.models.user import User
from app.schemas.admin_internship import InternshipReviewRequest
from app.schemas.internship import InternshipListResponse, InternshipResponse


def _get_org_name(db: Session, org_id: int) -> str | None:
    return db.scalar(
        select(func.coalesce(OrganizationProfile.organization_name, User.full_name))
        .select_from(User)
        .outerjoin(OrganizationProfile, User.id == OrganizationProfile.user_id)
        .where(User.id == org_id)
    )


def _to_response(
    p: Internship,
    org_name: str | None,
    applicant_count: int = 0,
    now: datetime | None = None,
) -> InternshipResponse:
    current_time = now or datetime.now(UTC)
    is_open = p.status == InternshipStatus.OPEN
    return InternshipResponse(
        id=p.id,
        organization_id=p.organization_id,
        organization_name=org_name,
        title=p.title,
        description=p.description,
        requirements=p.requirements,
        location=p.location,
        work_mode=p.work_mode,
        duration_weeks=p.duration_weeks,
        application_deadline=p.application_deadline,
        status=p.status,
        created_at=p.created_at,
        updated_at=p.updated_at,
        applicant_count=applicant_count,
        applications_accepted=(is_open and p.application_deadline > current_time),
        review_note=p.review_note,
        reviewed_at=p.reviewed_at,
        reviewed_by=p.reviewed_by,
    )


def list_admin_internships(
    db: Session,
    status: InternshipStatus | None = None,
    limit: int = 20,
    offset: int = 0,
) -> InternshipListResponse:
    """List postings for administrative review ordered oldest first."""
    target_status = status if status is not None else InternshipStatus.PENDING_REVIEW
    clamped_limit = min(max(limit, 1), 100)
    clamped_offset = max(offset, 0)
    now = datetime.now(UTC)

    org_col = func.coalesce(OrganizationProfile.organization_name, User.full_name)
    stmt = (
        select(Internship, org_col.label("org_name"))
        .join(User, Internship.organization_id == User.id)
        .outerjoin(OrganizationProfile, User.id == OrganizationProfile.user_id)
        .where(Internship.status == target_status)
    )
    count_stmt = select(func.count(Internship.id)).where(Internship.status == target_status)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(Internship.created_at.asc()).offset(clamped_offset).limit(clamped_limit)
    ).all()

    items = [_to_response(p, org_name, now=now) for p, org_name in rows]
    return InternshipListResponse(
        items=items, total=total, limit=clamped_limit, offset=clamped_offset
    )


def review_internship(
    db: Session,
    internship_id: int,
    reviewer_id: int,
    payload: InternshipReviewRequest,
) -> InternshipResponse:
    """Approve or reject a pending posting, or take down an active open posting."""
    p = db.scalar(select(Internship).where(Internship.id == internship_id))
    if not p:
        raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")

    if p.status == InternshipStatus.PENDING_REVIEW:
        if payload.decision == "approved":
            p.status = InternshipStatus.OPEN
        else:
            p.status = InternshipStatus.REJECTED
    elif p.status == InternshipStatus.OPEN:
        if payload.decision == "rejected":
            p.status = InternshipStatus.REJECTED
        else:
            raise ConflictException(message="Posting is already open", code="ALREADY_OPEN")
    else:
        raise ConflictException(
            message=f"Cannot review an internship in {p.status.value} status",
            code="INVALID_STATUS_TRANSITION",
        )

    p.reviewed_by = reviewer_id
    p.reviewed_at = datetime.now(UTC)
    p.review_note = payload.review_note

    db.commit()
    db.refresh(p)
    count = db.scalar(select(func.count(Application.id)).where(Application.posting_id == p.id)) or 0
    return _to_response(p, _get_org_name(db, p.organization_id), applicant_count=count)
