"""Domain service for aggregating student dashboard metrics."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship
from app.models.organization_profile import OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import User
from app.schemas.dashboard_student import (
    StudentApplicationRecentItem,
    StudentApplicationsSummary,
    StudentDashboardResponse,
)
from app.services.dashboard_student_academics import (
    get_student_course_progress,
    get_student_due_next,
    get_student_recent_grades,
)


def get_student_applications_summary(db: Session, student_id: int) -> StudentApplicationsSummary:
    """Fetch aggregated application status counts and latest 3 applications."""
    app_counts_stmt = (
        select(Application.status, func.count(Application.id).label("count"))
        .where(Application.student_id == student_id)
        .group_by(Application.status)
    )
    app_counts_map = {status.value: 0 for status in ApplicationStatus}
    for row in db.execute(app_counts_stmt).all():
        key = row.status.value if hasattr(row.status, "value") else str(row.status)
        app_counts_map[key] = row.count

    recent_apps_stmt = (
        select(
            Application.id,
            Application.posting_id,
            Internship.title.label("posting_title"),
            func.coalesce(
                OrganizationProfile.organization_name,
                User.full_name,
            ).label("organization_name"),
            Application.status,
            Application.created_at.label("applied_at"),
        )
        .join(Internship, Application.posting_id == Internship.id)
        .join(User, Internship.organization_id == User.id)
        .outerjoin(OrganizationProfile, OrganizationProfile.user_id == User.id)
        .where(Application.student_id == student_id)
        .order_by(Application.created_at.desc(), Application.id.desc())
        .limit(3)
    )
    recent_apps = [
        StudentApplicationRecentItem(
            id=row.id,
            posting_id=row.posting_id,
            posting_title=row.posting_title,
            organization_name=row.organization_name,
            status=row.status.value if hasattr(row.status, "value") else str(row.status),
            applied_at=row.applied_at,
        )
        for row in db.execute(recent_apps_stmt).all()
    ]
    return StudentApplicationsSummary(
        counts_by_status=app_counts_map,
        recent=recent_apps,
    )


def is_student_profile_complete(db: Session, student_id: int) -> bool:
    """Check if student profile has university and department populated."""
    profile = db.scalar(select(StudentProfile).where(StudentProfile.user_id == student_id))
    return bool(
        profile
        and profile.university
        and profile.university.strip()
        and profile.department
        and profile.department.strip()
    )


def get_student_dashboard(db: Session, student_id: int) -> StudentDashboardResponse:
    """Aggregate dashboard metrics for an authenticated student."""
    return StudentDashboardResponse(
        due_next=get_student_due_next(db, student_id),
        recent_grades=get_student_recent_grades(db, student_id),
        courses=get_student_course_progress(db, student_id),
        applications=get_student_applications_summary(db, student_id),
        profile_complete=is_student_profile_complete(db, student_id),
    )
