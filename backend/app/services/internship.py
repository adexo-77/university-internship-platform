"""Business logic and database operations for internship posting management."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.application import Application
from app.models.internship import Internship, InternshipStatus
from app.models.organization_profile import OrganizationProfile
from app.models.user import User
from app.schemas.internship import (
    InternshipCreate,
    InternshipResponse,
    InternshipUpdate,
)


def _get_org_name(db: Session, org_id: int) -> str | None:
    return db.scalar(
        select(func.coalesce(OrganizationProfile.organization_name, User.full_name))
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
    )


def create_internship(
    db: Session, organization_id: int, payload: InternshipCreate
) -> InternshipResponse:
    """Create a new internship posting in draft status."""
    posting = Internship(
        organization_id=organization_id,
        title=payload.title,
        description=payload.description,
        requirements=payload.requirements,
        location=payload.location,
        work_mode=payload.work_mode,
        duration_weeks=payload.duration_weeks,
        application_deadline=payload.application_deadline,
        status=InternshipStatus.DRAFT,
    )
    db.add(posting)
    db.commit()
    db.refresh(posting)
    return _to_response(posting, _get_org_name(db, organization_id))


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
    return [_to_response(p, org_name, count, now=now) for p, count in db.execute(stmt).all()]


def update_internship(
    db: Session, internship_id: int, payload: InternshipUpdate, current_user: User
) -> InternshipResponse:
    """Update internship posting fields and enforce strict status transition rules."""
    p = db.scalar(select(Internship).where(Internship.id == internship_id))
    if not p:
        raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")
    if p.organization_id != current_user.id:
        raise ForbiddenException(
            message="Only the owning organization can update this posting", code="FORBIDDEN"
        )
    if p.status == InternshipStatus.CLOSED:
        raise ConflictException(
            message="A closed internship posting cannot be edited", code="POSTING_CLOSED"
        )

    if payload.status is not None and payload.status != p.status:
        valid_moves = {
            (InternshipStatus.DRAFT, InternshipStatus.OPEN),
            (InternshipStatus.OPEN, InternshipStatus.CLOSED),
        }
        if (p.status, payload.status) not in valid_moves:
            raise ConflictException(
                message=f"Invalid status transition from {p.status} to {payload.status}",
                code="INVALID_STATUS_TRANSITION",
            )
        p.status = payload.status

    for field in (
        "title",
        "description",
        "requirements",
        "location",
        "work_mode",
        "duration_weeks",
        "application_deadline",
    ):
        val = getattr(payload, field)
        if val is not None:
            setattr(p, field, val)

    db.commit()
    db.refresh(p)
    count = db.scalar(select(func.count(Application.id)).where(Application.posting_id == p.id)) or 0
    return _to_response(p, _get_org_name(db, p.organization_id), applicant_count=count)
