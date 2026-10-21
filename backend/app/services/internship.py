"""Business logic and database operations for internship posting management."""

from datetime import UTC, datetime

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
from app.services.internship_deadline import (
    check_deadline_cap,
    to_internship_response,
    update_posting_deadline,
)

CONTENT_FIELDS = (
    "title",
    "description",
    "requirements",
    "location",
    "work_mode",
    "duration_weeks",
)


def _get_org_name(db: Session, org_id: int) -> str | None:
    return db.scalar(
        select(func.coalesce(OrganizationProfile.organization_name, User.full_name))
        .select_from(User)
        .outerjoin(OrganizationProfile, User.id == OrganizationProfile.user_id)
        .where(User.id == org_id)
    )


def create_internship(
    db: Session, organization_id: int, payload: InternshipCreate
) -> InternshipResponse:
    """Create a new internship posting in draft status."""
    check_deadline_cap(payload.application_deadline)
    posting = Internship(
        organization_id=organization_id,
        status=InternshipStatus.DRAFT,
        **payload.model_dump(),
    )
    db.add(posting)
    db.commit()
    db.refresh(posting)
    return to_internship_response(posting, _get_org_name(db, organization_id), include_review=True)


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
        to_internship_response(p, org_name, count, now=now, include_review=True)
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
    return to_internship_response(
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

    if p.status == InternshipStatus.OPEN:
        for field in CONTENT_FIELDS:
            val = getattr(payload, field)
            if val is not None and val != getattr(p, field):
                raise ConflictException(
                    message=(
                        "Cannot edit content of an open posting; only deadline extension is allowed"
                    ),
                    code="CONTENT_LOCKED",
                )
    elif p.status in (InternshipStatus.DRAFT, InternshipStatus.REJECTED):
        for field in CONTENT_FIELDS:
            val = getattr(payload, field)
            if val is not None:
                setattr(p, field, val)

    if payload.application_deadline is not None:
        update_posting_deadline(p, payload.application_deadline)

    return _save_and_response(db, p)
