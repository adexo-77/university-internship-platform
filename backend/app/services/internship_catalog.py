"""Internship catalog queries, search, pagination, and visibility logic."""

from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, NotFoundException
from app.models.application import Application
from app.models.internship import Internship, InternshipStatus, InternshipWorkMode
from app.models.organization_profile import OrganizationProfile
from app.models.user import User, UserRole
from app.schemas.internship import (
    InternshipListResponse,
    InternshipResponse,
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
    applied: bool | None = None,
    app_status: str | None = None,
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
        applied=applied,
        application_status=app_status,
    )


def list_internships(
    db: Session,
    current_user: User,
    q: str | None = None,
    work_mode: InternshipWorkMode | None = None,
    limit: int = 20,
    offset: int = 0,
) -> InternshipListResponse:
    """Browse catalog of internship postings with filters and pagination."""
    if current_user.role not in (UserRole.STUDENT, UserRole.ADMIN):
        raise ForbiddenException(
            message="Organizations and instructors cannot browse the internship catalogue",
            code="FORBIDDEN",
        )

    clamped_limit = min(max(limit, 1), 100)
    clamped_offset = max(offset, 0)
    now = datetime.now(UTC)

    org_col = func.coalesce(OrganizationProfile.organization_name, User.full_name)
    stmt = (
        select(Internship, org_col.label("org_name"))
        .join(User, Internship.organization_id == User.id)
        .outerjoin(OrganizationProfile, User.id == OrganizationProfile.user_id)
    )
    count_stmt = (
        select(func.count(Internship.id))
        .join(User, Internship.organization_id == User.id)
        .outerjoin(OrganizationProfile, User.id == OrganizationProfile.user_id)
    )

    if current_user.role == UserRole.STUDENT:
        stmt = stmt.where(Internship.status == InternshipStatus.OPEN)
        count_stmt = count_stmt.where(Internship.status == InternshipStatus.OPEN)

    if work_mode is not None:
        stmt = stmt.where(Internship.work_mode == work_mode)
        count_stmt = count_stmt.where(Internship.work_mode == work_mode)

    if q and q.strip():
        term = f"%{q.strip()}%"
        search = or_(
            Internship.title.ilike(term),
            OrganizationProfile.organization_name.ilike(term),
            User.full_name.ilike(term),
        )
        stmt, count_stmt = stmt.where(search), count_stmt.where(search)

    total = db.scalar(count_stmt) or 0
    rows = db.execute(
        stmt.order_by(Internship.created_at.desc()).offset(clamped_offset).limit(clamped_limit)
    ).all()

    app_map: dict[int, str] = {}
    if current_user.role == UserRole.STUDENT and rows:
        p_ids = [p.id for p, _ in rows]
        app_rows = db.execute(
            select(Application.posting_id, Application.status).where(
                Application.student_id == current_user.id, Application.posting_id.in_(p_ids)
            )
        ).all()
        app_map = {p_id: status.value for p_id, status in app_rows}

    items = [
        _to_response(
            p,
            org_name,
            applied=(p.id in app_map) if current_user.role == UserRole.STUDENT else None,
            app_status=app_map.get(p.id),
            now=now,
        )
        for p, org_name in rows
    ]
    return InternshipListResponse(
        items=items, total=total, limit=clamped_limit, offset=clamped_offset
    )


def get_internship_by_id(db: Session, internship_id: int, current_user: User) -> InternshipResponse:
    """Retrieve detailed information for a single internship posting."""
    p = db.scalar(select(Internship).where(Internship.id == internship_id))
    if not p:
        raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")

    is_owner = p.organization_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN
    if current_user.role == UserRole.STUDENT:
        if p.status != InternshipStatus.OPEN:
            raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")
    elif current_user.role == UserRole.ORGANIZATION:
        if not is_owner:
            raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")
    elif not is_admin:
        raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")

    applied, app_status = None, None
    if current_user.role == UserRole.STUDENT:
        app = db.scalar(
            select(Application).where(
                Application.posting_id == p.id, Application.student_id == current_user.id
            )
        )
        applied = app is not None
        app_status = app.status.value if app else None

    count = 0
    if is_owner or is_admin:
        count = (
            db.scalar(select(func.count(Application.id)).where(Application.posting_id == p.id)) or 0
        )

    return _to_response(
        p,
        _get_org_name(db, p.organization_id),
        applicant_count=count,
        applied=applied,
        app_status=app_status,
    )
