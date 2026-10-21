"""Integration tests for the administrator platform dashboard endpoint."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import ApplicationStatus
from app.models.course import Course, CourseStatus
from app.models.internship import InternshipStatus
from app.models.organization_profile import ApprovalStatus
from app.models.user import UserRole
from tests.factories import (
    create_test_application,
    create_test_internship,
    create_test_organization,
    create_test_student,
    create_test_user,
    login_test_user,
)


def test_admin_dashboard_role_guards(real_db_client: TestClient, real_db_session: Session) -> None:
    """Only authenticated administrators may access the admin dashboard."""
    real_db_client.cookies.clear()
    assert real_db_client.get("/api/dashboard/admin").status_code == 401

    for role in [UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORGANIZATION]:
        u = create_test_user(real_db_session, f"admin_guard_{role.value}@test.com", role)
        login_test_user(real_db_client, u.email)
        assert real_db_client.get("/api/dashboard/admin").status_code == 403

    admin = create_test_user(real_db_session, "admin_guard_ok@test.com", UserRole.ADMIN)
    login_test_user(real_db_client, admin.email)
    assert real_db_client.get("/api/dashboard/admin").status_code == 200


def test_admin_dashboard_metrics_counts(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Administrator dashboard accurately reports platform activity and pending moderation items."""
    admin = create_test_user(real_db_session, "adm_met_1@test.com", UserRole.ADMIN)
    student, _ = create_test_student(real_db_session, "adm_met_stud@test.com")
    inst = create_test_user(real_db_session, "adm_met_inst@test.com", UserRole.INSTRUCTOR)

    # 1 approved org, 1 pending org
    org_approved, _ = create_test_organization(
        real_db_session, "adm_met_org_app@test.com", approval_status=ApprovalStatus.APPROVED
    )
    create_test_organization(
        real_db_session, "adm_met_org_pend@test.com", approval_status=ApprovalStatus.PENDING
    )

    # Inactive user
    inactive_user = create_test_user(real_db_session, "adm_met_inact@test.com", UserRole.STUDENT)
    inactive_user.is_active = False
    real_db_session.commit()

    # Courses: 1 published, 1 draft
    c_pub = Course(instructor_id=inst.id, title="Algorithms", status=CourseStatus.PUBLISHED)
    c_draft = Course(instructor_id=inst.id, title="Compilers", status=CourseStatus.DRAFT)
    real_db_session.add_all([c_pub, c_draft])
    real_db_session.commit()

    # Internships: 1 open, 1 pending_review, 1 draft
    p_open = create_test_internship(
        real_db_session, org_approved, title="Open Posting", status=InternshipStatus.OPEN
    )
    create_test_internship(
        real_db_session,
        org_approved,
        title="Pending Posting",
        status=InternshipStatus.PENDING_REVIEW,
    )
    create_test_internship(
        real_db_session, org_approved, title="Draft Posting", status=InternshipStatus.DRAFT
    )

    # Applications: 1 submitted
    create_test_application(real_db_session, p_open, student, status=ApplicationStatus.SUBMITTED)

    login_test_user(real_db_client, admin.email)
    resp = real_db_client.get("/api/dashboard/admin")
    assert resp.status_code == 200
    data = resp.json()

    # Active and role counts
    assert data["users_by_role"]["admin"] >= 1
    assert data["users_by_role"]["student"] >= 2
    assert data["users_by_role"]["instructor"] >= 1
    assert data["users_by_role"]["organization"] >= 2
    assert data["users_total_count"] >= 6
    assert data["users_active_count"] < data["users_total_count"]

    # Organizations pending approval
    assert data["organizations_pending_approval"] >= 1

    # Postings pending review & open internships
    assert data["postings_pending_review"] >= 1
    assert data["open_internships"] >= 1

    # Courses
    assert data["courses_by_status"]["published"] >= 1
    assert data["courses_by_status"]["draft"] >= 1

    # Applications
    assert data["applications_by_status"]["submitted"] >= 1
