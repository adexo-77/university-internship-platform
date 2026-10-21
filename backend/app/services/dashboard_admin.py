"""Domain service for aggregating administrator platform dashboard metrics."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.course import Course, CourseStatus
from app.models.internship import Internship, InternshipStatus
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.user import User, UserRole
from app.schemas.dashboard_admin import AdminDashboardResponse


def get_admin_dashboard(db: Session) -> AdminDashboardResponse:
    """Aggregate high-level platform health metrics for administrators."""
    # 1. Users by role & active count
    user_roles_stmt = select(User.role, func.count(User.id).label("count")).group_by(User.role)
    users_by_role = {role.value: 0 for role in UserRole}
    for row in db.execute(user_roles_stmt).all():
        key = row.role.value if hasattr(row.role, "value") else str(row.role)
        users_by_role[key] = row.count

    active_count = db.scalar(select(func.count(User.id)).where(User.is_active.is_(True))) or 0
    total_users = sum(users_by_role.values())

    # 2. Organizations pending approval
    orgs_pending = (
        db.scalar(
            select(func.count(OrganizationProfile.id)).where(
                OrganizationProfile.approval_status == ApprovalStatus.PENDING
            )
        )
        or 0
    )

    # 3. Postings pending review & open internships
    postings_stmt = (
        select(Internship.status, func.count(Internship.id).label("count"))
        .where(Internship.status.in_([InternshipStatus.PENDING_REVIEW, InternshipStatus.OPEN]))
        .group_by(Internship.status)
    )
    postings_map = {
        row.status.value if hasattr(row.status, "value") else str(row.status): row.count
        for row in db.execute(postings_stmt).all()
    }
    pending_review_count = postings_map.get(InternshipStatus.PENDING_REVIEW.value, 0)
    open_internships_count = postings_map.get(InternshipStatus.OPEN.value, 0)

    # 4. Courses by status
    courses_stmt = select(Course.status, func.count(Course.id).label("count")).group_by(
        Course.status
    )
    courses_by_status = {status.value: 0 for status in CourseStatus}
    for row in db.execute(courses_stmt).all():
        key = row.status.value if hasattr(row.status, "value") else str(row.status)
        courses_by_status[key] = row.count

    # 5. Applications by status
    apps_stmt = select(Application.status, func.count(Application.id).label("count")).group_by(
        Application.status
    )
    apps_by_status = {status.value: 0 for status in ApplicationStatus}
    for row in db.execute(apps_stmt).all():
        key = row.status.value if hasattr(row.status, "value") else str(row.status)
        apps_by_status[key] = row.count

    return AdminDashboardResponse(
        users_by_role=users_by_role,
        users_active_count=active_count,
        users_total_count=total_users,
        organizations_pending_approval=orgs_pending,
        postings_pending_review=pending_review_count,
        open_internships=open_internships_count,
        courses_by_status=courses_by_status,
        applications_by_status=apps_by_status,
    )
