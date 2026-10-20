"""Business logic and database operations for internship posting management."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.application import Application
from app.models.internship import Internship, InternshipStatus
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.user import User
from app.schemas.internship import (
    InternshipCreate,
    InternshipResponse,
    InternshipUpdate,
)

MAX_DEADLINE_DAYS = 90


def _ensure_utc(dt: datetime) -> datetime:
    return dt.astimezone(UTC) if dt.tzinfo is not None else dt.replace(tzinfo=UTC)


def _check_deadline_cap(deadline: datetime, p: Internship | None = None) -> None:
    dl = _ensure_utc(deadline)
    ref = (
        _ensure_utc(p.reviewed_at)
        if p and p.status == InternshipStatus.OPEN and p.reviewed_at
        else datetime.now(UTC)
    )
    max_dl = ref + timedelta(days=MAX_DEADLINE_DAYS)
    if dl > max_dl:
        max_str = max_dl.strftime("%d %b %Y")
        raise ConflictException(
            message=f"Application deadline cannot be later than {max_str}",
            code="DEADLINE_CAP_EXCEEDED",
        )


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
    include_review: bool = False,
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
        review_note=p.review_note if include_review else None,
        reviewed_at=p.reviewed_at if include_review else None,
        reviewed_by=p.reviewed_by if include_review else None,
    )


def create_internship(
    db: Session, organization_id: int, payload: InternshipCreate
) -> InternshipResponse:
    """Create a new internship posting in draft status."""
    _check_deadline_cap(payload.application_deadline)
    posting = Internship(
        organization_id=organization_id,
        status=InternshipStatus.DRAFT,
        **payload.model_dump(),
    )
    db.add(posting)
    db.commit()
    db.refresh(posting)
    return _to_response(posting, _get_org_name(db, organization_id), include_review=True)


def get_organization_internships(db: Session, organization_id: int) -> list[InternshipResponse]:
    """Retrieve all internship postings owned by the organization with applicant counts."""
    org_name = _get_org_name(db, organization_id)
    now = datetime.now(UTC)
    stmt = (
        select(Internship, func.count(Application.id).label("applicant_count"))
        .outerjoin(Application, Internship.id == Application.posting_id)
        .where(Internship.organization_id == organization_id)
        .group_by(Internship.id)
        .order_by(Internship.created_at.desc())
    )
    return [
        _to_response(p, org_name, count, now=now, include_review=True)
        for p, count in db.execute(stmt).all()
    ]


def _get_owned_posting(db: Session, internship_id: int, user_id: int) -> Internship:
    p = db.scalar(select(Internship).where(Internship.id == internship_id))
    if not p or p.organization_id != user_id:
        raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")
    return p


def _save_and_response(db: Session, p: Internship) -> InternshipResponse:
    db.commit()
    db.refresh(p)
    count = db.scalar(select(func.count(Application.id)).where(Application.posting_id == p.id)) or 0
    return _to_response(
        p, _get_org_name(db, p.organization_id), applicant_count=count, include_review=True
    )


def _transition_posting(
    db: Session, p: Internship, new_status: InternshipStatus
) -> InternshipResponse:
    p.status = new_status
    return _save_and_response(db, p)


def submit_internship(db: Session, internship_id: int, current_user: User) -> InternshipResponse:
    """Submit a draft or rejected posting for administrative review."""
    p = _get_owned_posting(db, internship_id, current_user.id)
    if p.status not in (InternshipStatus.DRAFT, InternshipStatus.REJECTED):
        raise ConflictException(
            message=f"Cannot submit an internship in {p.status.value} status",
            code="INVALID_STATUS_TRANSITION",
        )
    org_profile = db.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == current_user.id)
    )
    if not org_profile or org_profile.approval_status != ApprovalStatus.APPROVED:
        raise ConflictException(
            message="Your organization must be approved before you can submit internships",
            code="ORGANIZATION_NOT_APPROVED",
        )
    return _transition_posting(db, p, InternshipStatus.PENDING_REVIEW)


def withdraw_internship(db: Session, internship_id: int, current_user: User) -> InternshipResponse:
    """Withdraw a pending_review posting back to draft status for editing."""
    p = _get_owned_posting(db, internship_id, current_user.id)
    if p.status != InternshipStatus.PENDING_REVIEW:
        raise ConflictException(
            message=f"Cannot withdraw an internship in {p.status.value} status",
            code="INVALID_STATUS_TRANSITION",
        )
    return _transition_posting(db, p, InternshipStatus.DRAFT)


def close_internship(db: Session, internship_id: int, current_user: User) -> InternshipResponse:
    """Close an open internship posting."""
    p = _get_owned_posting(db, internship_id, current_user.id)
    if p.status != InternshipStatus.OPEN:
        raise ConflictException(
            message=f"Cannot close an internship in {p.status.value} status",
            code="INVALID_STATUS_TRANSITION",
        )
    return _transition_posting(db, p, InternshipStatus.CLOSED)


def update_internship(
    db: Session, internship_id: int, payload: InternshipUpdate, current_user: User
) -> InternshipResponse:
    """Update internship posting fields and enforce strict status transition rules."""
    p = _get_owned_posting(db, internship_id, current_user.id)
    if p.status == InternshipStatus.CLOSED:
        raise ConflictException(
            message="A closed internship posting cannot be edited", code="POSTING_CLOSED"
        )
    if p.status == InternshipStatus.PENDING_REVIEW:
        raise ConflictException(
            message="Posting is pending review and cannot be edited. Withdraw to draft to edit.",
            code="POSTING_LOCKED",
        )

    if payload.status is not None:
        if payload.status == InternshipStatus.OPEN:
            raise ConflictException(
                message="Submit for review instead", code="SUBMIT_FOR_REVIEW_REQUIRED"
            )
        if payload.status != p.status:
            if (p.status, payload.status) != (InternshipStatus.OPEN, InternshipStatus.CLOSED):
                raise ConflictException(
                    message=(
                        f"Invalid status transition from {p.status.value} to {payload.status.value}"
                    ),
                    code="INVALID_STATUS_TRANSITION",
                )
            p.status = payload.status

    content_fields = (
        "title",
        "description",
        "requirements",
        "location",
        "work_mode",
        "duration_weeks",
    )
    if p.status == InternshipStatus.OPEN:
        for field in content_fields:
            val = getattr(payload, field)
            if val is not None and val != getattr(p, field):
                raise ConflictException(
                    message=(
                        "Cannot edit content of an open posting; only deadline extension is allowed"
                    ),
                    code="CONTENT_LOCKED",
                )
        if payload.application_deadline is not None:
            new_dl = _ensure_utc(payload.application_deadline)
            cur_dl = _ensure_utc(p.application_deadline)
            if new_dl <= cur_dl:
                raise ConflictException(
                    message="Application deadline can only be extended, not shortened",
                    code="DEADLINE_CANNOT_BE_SHORTENED",
                )
            _check_deadline_cap(new_dl, p)
            p.application_deadline = new_dl
    elif p.status in (InternshipStatus.DRAFT, InternshipStatus.REJECTED):
        for field in content_fields:
            val = getattr(payload, field)
            if val is not None:
                setattr(p, field, val)
        if payload.application_deadline is not None:
            _check_deadline_cap(payload.application_deadline, p)
            p.application_deadline = payload.application_deadline

    return _save_and_response(db, p)
