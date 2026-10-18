"""Business logic and database operations for internship applications."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus
from app.models.organization_profile import OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import User, UserRole
from app.schemas.application import (
    ApplicantProfile,
    ApplicationCreate,
    ApplicationDecision,
    ApplicationResponse,
)


def _get_org_name(db: Session, org_id: int) -> str | None:
    return db.scalar(
        select(func.coalesce(OrganizationProfile.organization_name, User.full_name))
        .select_from(User)
        .outerjoin(OrganizationProfile, User.id == OrganizationProfile.user_id)
        .where(User.id == org_id)
    )


def _to_applicant(u: User, p: StudentProfile | None) -> ApplicantProfile:
    return ApplicantProfile(
        user_id=u.id,
        full_name=u.full_name,
        email=u.email,
        university=p.university if p else None,
        department=p.department if p else None,
        year_of_study=p.year_of_study if p else None,
        skills=p.skills if p else [],
        bio=p.bio if p else None,
    )


def _to_response(
    a: Application,
    posting_title: str | None = None,
    org_name: str | None = None,
    applicant: ApplicantProfile | None = None,
) -> ApplicationResponse:
    res = ApplicationResponse.model_validate(a)
    res.posting_title = posting_title
    res.organization_name = org_name
    res.applicant = applicant
    return res


def apply_to_internship(
    db: Session, posting_id: int, student_id: int, payload: ApplicationCreate
) -> ApplicationResponse:
    """Submit an application to an open internship posting before deadline."""
    p = db.scalar(select(Internship).where(Internship.id == posting_id))
    if not p:
        raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")
    if p.status != InternshipStatus.OPEN:
        raise ConflictException(
            message="Applications can only be submitted to open postings", code="POSTING_NOT_OPEN"
        )
    if p.application_deadline <= datetime.now(UTC):
        raise ConflictException(message="Application deadline has passed", code="DEADLINE_PASSED")

    prof = db.scalar(select(StudentProfile).where(StudentProfile.user_id == student_id))
    if not (
        prof
        and prof.university
        and prof.department
        and prof.university.strip()
        and prof.department.strip()
    ):
        raise ConflictException(
            message="Complete your profile before applying", code="INCOMPLETE_PROFILE"
        )

    if db.scalar(
        select(Application.id).where(
            Application.posting_id == posting_id, Application.student_id == student_id
        )
    ):
        raise ConflictException(
            message="You have already applied to this internship", code="DUPLICATE_APPLICATION"
        )

    app = Application(
        posting_id=posting_id,
        student_id=student_id,
        cover_letter=payload.cover_letter,
        status=ApplicationStatus.SUBMITTED,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return _to_response(app, p.title, _get_org_name(db, p.organization_id))


def get_student_applications(db: Session, student_id: int) -> list[ApplicationResponse]:
    """Retrieve all applications submitted by the authenticated student."""
    org_col = func.coalesce(OrganizationProfile.organization_name, User.full_name)
    stmt = (
        select(Application, Internship.title, org_col.label("org_name"))
        .join(Internship, Application.posting_id == Internship.id)
        .join(User, Internship.organization_id == User.id)
        .outerjoin(OrganizationProfile, User.id == OrganizationProfile.user_id)
        .where(Application.student_id == student_id)
        .order_by(Application.created_at.desc())
    )
    return [_to_response(a, title, org) for a, title, org in db.execute(stmt).all()]


def withdraw_application(db: Session, application_id: int, student_id: int) -> ApplicationResponse:
    """Withdraw an application while in submitted or shortlisted status."""
    app = db.scalar(select(Application).where(Application.id == application_id))
    if not app or app.student_id != student_id:
        raise NotFoundException(message="Application not found", code="NOT_FOUND")

    if app.status not in (ApplicationStatus.SUBMITTED, ApplicationStatus.SHORTLISTED):
        raise ConflictException(
            message=f"Cannot withdraw an application that is already {app.status.value}",
            code="CANNOT_WITHDRAW",
        )

    app.status = ApplicationStatus.WITHDRAWN
    db.commit()
    db.refresh(app)
    p = db.scalar(select(Internship).where(Internship.id == app.posting_id))
    org_name = _get_org_name(db, p.organization_id) if p else None
    return _to_response(app, p.title if p else None, org_name)


def get_internship_applications(
    db: Session, posting_id: int, current_user: User, status: ApplicationStatus | None = None
) -> list[ApplicationResponse]:
    """Retrieve applicant roster for a posting (owner organization or admin)."""
    p = db.scalar(select(Internship).where(Internship.id == posting_id))
    if not p:
        raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")

    is_admin = current_user.role == UserRole.ADMIN
    if not (p.organization_id == current_user.id or is_admin):
        raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")

    stmt = (
        select(Application, User, StudentProfile)
        .join(User, Application.student_id == User.id)
        .outerjoin(StudentProfile, User.id == StudentProfile.user_id)
        .where(Application.posting_id == posting_id)
    )
    if status is not None:
        stmt = stmt.where(Application.status == status)

    org_name = _get_org_name(db, p.organization_id)
    return [
        _to_response(a, p.title, org_name, _to_applicant(u, prof))
        for a, u, prof in db.execute(stmt.order_by(Application.created_at.desc())).all()
    ]


def get_application_by_id(
    db: Session, application_id: int, current_user: User
) -> ApplicationResponse:
    """Retrieve application detail if authorized (student owner, posting owner, or admin)."""
    row = db.execute(
        select(Application, Internship, User, StudentProfile)
        .join(Internship, Application.posting_id == Internship.id)
        .join(User, Application.student_id == User.id)
        .outerjoin(StudentProfile, User.id == StudentProfile.user_id)
        .where(Application.id == application_id)
    ).first()

    if not row:
        raise NotFoundException(message="Application not found", code="NOT_FOUND")

    app, p, user, prof = row
    is_owner = app.student_id == current_user.id or p.organization_id == current_user.id
    if not (is_owner or current_user.role == UserRole.ADMIN):
        raise NotFoundException(message="Application not found", code="NOT_FOUND")

    show_applicant = p.organization_id == current_user.id or current_user.role == UserRole.ADMIN
    applicant = _to_applicant(user, prof) if show_applicant else None
    return _to_response(app, p.title, _get_org_name(db, p.organization_id), applicant)


def decide_application(
    db: Session, application_id: int, payload: ApplicationDecision, current_user: User
) -> ApplicationResponse:
    """Record an organization decision on an application with state machine rules."""
    if current_user.role != UserRole.ORGANIZATION:
        raise ForbiddenException(
            message="Only the owning organization can make a decision", code="FORBIDDEN"
        )

    row = db.execute(
        select(Application, Internship)
        .join(Internship, Application.posting_id == Internship.id)
        .where(Application.id == application_id)
    ).first()

    if not row or row[1].organization_id != current_user.id:
        raise NotFoundException(message="Application not found", code="NOT_FOUND")

    app, p = row
    if app.status == ApplicationStatus.WITHDRAWN:
        raise ConflictException(
            message="Withdrawn applications cannot be decided", code="APPLICATION_WITHDRAWN"
        )
    if app.status in (ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED):
        raise ConflictException(
            message="Accepted and rejected decisions are final", code="DECISION_FINAL"
        )

    valid_moves: dict[ApplicationStatus, set[ApplicationStatus]] = {
        ApplicationStatus.SUBMITTED: {
            ApplicationStatus.SHORTLISTED,
            ApplicationStatus.ACCEPTED,
            ApplicationStatus.REJECTED,
        },
        ApplicationStatus.SHORTLISTED: {ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED},
    }
    allowed = valid_moves.get(app.status, set())
    if payload.status not in allowed:
        msg = f"Invalid decision transition from {app.status.value} to {payload.status.value}"
        raise ConflictException(message=msg, code="INVALID_DECISION_TRANSITION")

    app.status = payload.status
    app.decision_message = payload.decision_message
    app.decided_at = datetime.now(UTC)
    db.commit()
    db.refresh(app)
    return _to_response(app, p.title, _get_org_name(db, p.organization_id))
