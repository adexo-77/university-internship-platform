"""Business logic and database operations for internship applications."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus
from app.models.notification import NotificationKind
from app.models.organization_profile import OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import User, UserRole
from app.schemas.application import (
    ApplicationCreate,
    ApplicationDecision,
    ApplicationResponse,
)
from app.services.application_helpers import get_org_name, to_applicant, to_response
from app.services.notification import create_notification


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
    db.flush()
    create_notification(
        db,
        user_id=p.organization_id,
        actor_id=student_id,
        kind=NotificationKind.APPLICATION_RECEIVED,
        title=f"New Application: {p.title}",
        message=f"A new application was received for '{p.title}'.",
        link_path=f"/internships/{p.id}",
    )
    db.commit()
    db.refresh(app)
    return to_response(app, p.title, get_org_name(db, p.organization_id))


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
    return [to_response(a, title, org) for a, title, org in db.execute(stmt).all()]


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
    org_name = get_org_name(db, p.organization_id) if p else None
    return to_response(app, p.title if p else None, org_name)


def get_internship_applications(
    db: Session, posting_id: int, current_user: User, status: ApplicationStatus | None = None
) -> list[ApplicationResponse]:
    """Retrieve applicant roster for a posting (owner organization or admin)."""
    p = db.scalar(select(Internship).where(Internship.id == posting_id))
    if not p:
        raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")

    is_privileged = current_user.role in (UserRole.ADMIN, UserRole.COORDINATOR)
    if not (p.organization_id == current_user.id or is_privileged):
        raise NotFoundException(message="Internship posting not found", code="NOT_FOUND")

    stmt = (
        select(Application, User, StudentProfile)
        .join(User, Application.student_id == User.id)
        .outerjoin(StudentProfile, User.id == StudentProfile.user_id)
        .where(Application.posting_id == posting_id)
    )
    if status is not None:
        stmt = stmt.where(Application.status == status)

    org_name = get_org_name(db, p.organization_id)
    return [
        to_response(a, p.title, org_name, to_applicant(u, prof))
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
    is_privileged = current_user.role in (UserRole.ADMIN, UserRole.COORDINATOR)
    if not (is_owner or is_privileged):
        raise NotFoundException(message="Application not found", code="NOT_FOUND")

    show_applicant = p.organization_id == current_user.id or is_privileged
    applicant = to_applicant(user, prof) if show_applicant else None
    return to_response(app, p.title, get_org_name(db, p.organization_id), applicant)


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
    db.flush()
    msg_suffix = f": {payload.decision_message}" if payload.decision_message else "."
    create_notification(
        db,
        user_id=app.student_id,
        actor_id=current_user.id,
        kind=NotificationKind.APPLICATION_DECISION,
        title=f"Application {payload.status.value.capitalize()}: {p.title}",
        message=(
            f"Your application for '{p.title}' was marked as {payload.status.value}{msg_suffix}"
        ),
        link_path=f"/applications/{app.id}",
    )
    db.commit()
    db.refresh(app)
    return to_response(app, p.title, get_org_name(db, p.organization_id))
