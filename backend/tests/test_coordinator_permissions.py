"""Tests for coordinator role permissions and boundaries (real database)."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.internship import InternshipStatus
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.user import UserRole
from tests.factories import create_test_internship, create_test_user, login_test_user


def test_coordinator_can_list_and_decide_organization_approvals(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Coordinator can list organizations and approve or reject them with notes."""
    coord = create_test_user(real_db_session, "coord_org@example.com", UserRole.COORDINATOR)
    org1 = create_test_user(real_db_session, "org_to_appr@example.com", UserRole.ORGANIZATION)
    org2 = create_test_user(real_db_session, "org_to_rej@example.com", UserRole.ORGANIZATION)
    real_db_session.add_all(
        [
            OrganizationProfile(
                user_id=org1.id, organization_name="Org 1", approval_status=ApprovalStatus.PENDING
            ),
            OrganizationProfile(
                user_id=org2.id, organization_name="Org 2", approval_status=ApprovalStatus.PENDING
            ),
        ]
    )
    real_db_session.commit()

    login_test_user(real_db_client, coord.email)

    list_res = real_db_client.get("/api/admin/organizations")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 2

    appr_res = real_db_client.put(
        f"/api/admin/organizations/{org1.id}/approval",
        json={"approval_status": "approved", "approval_note": "Verified by coordinator"},
    )
    assert appr_res.status_code == 200
    assert appr_res.json()["approval_status"] == "approved"
    assert appr_res.json()["reviewed_by"] == coord.id

    rej_res = real_db_client.put(
        f"/api/admin/organizations/{org2.id}/approval",
        json={"approval_status": "rejected", "approval_note": "Incomplete papers"},
    )
    assert rej_res.status_code == 200
    assert rej_res.json()["approval_status"] == "rejected"
    assert rej_res.json()["reviewed_by"] == coord.id


def test_coordinator_can_review_and_take_down_postings(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Coordinator can review pending postings and take down published postings."""
    coord = create_test_user(real_db_session, "coord_review@example.com", UserRole.COORDINATOR)
    org = create_test_user(real_db_session, "org_posting@example.com", UserRole.ORGANIZATION)
    p_pending = create_test_internship(
        real_db_session, org, title="Pending Intern", status=InternshipStatus.PENDING_REVIEW
    )
    p_open = create_test_internship(
        real_db_session, org, title="Open Intern", status=InternshipStatus.OPEN
    )

    login_test_user(real_db_client, coord.email)

    q_res = real_db_client.get("/api/admin/internships")
    assert q_res.status_code == 200

    appr_res = real_db_client.put(
        f"/api/admin/internships/{p_pending.id}/review",
        json={"decision": "approved", "review_note": "Good to publish"},
    )
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "open"
    assert appr_res.json()["reviewed_by"] == coord.id

    td_res = real_db_client.put(
        f"/api/admin/internships/{p_open.id}/review",
        json={"decision": "rejected", "review_note": "Taken down due to violation"},
    )
    assert td_res.status_code == 200
    assert td_res.json()["status"] == "rejected"
    assert td_res.json()["reviewed_by"] == coord.id


def test_coordinator_can_read_applicants_read_only(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Coordinator can view posting applicants and application details (read-only)."""
    coord = create_test_user(real_db_session, "coord_appls@example.com", UserRole.COORDINATOR)
    org = create_test_user(real_db_session, "org_appls@example.com", UserRole.ORGANIZATION)
    student = create_test_user(real_db_session, "stud_appl@example.com", UserRole.STUDENT)
    posting = create_test_internship(real_db_session, org, status=InternshipStatus.OPEN)

    app = Application(
        posting_id=posting.id,
        student_id=student.id,
        cover_letter="Interested in the position.",
        status=ApplicationStatus.SUBMITTED,
    )
    real_db_session.add(app)
    real_db_session.commit()
    real_db_session.refresh(app)

    login_test_user(real_db_client, coord.email)

    roster_res = real_db_client.get(f"/api/internships/{posting.id}/applications")
    assert roster_res.status_code == 200
    assert len(roster_res.json()) >= 1

    detail_res = real_db_client.get(f"/api/applications/{app.id}")
    assert detail_res.status_code == 200
    assert detail_res.json()["cover_letter"] == "Interested in the position."

    # Coordinator cannot decide on the application (read-only for coordinator)
    decide_res = real_db_client.put(
        f"/api/applications/{app.id}/decision",
        json={"status": "accepted", "decision_message": "Not allowed"},
    )
    assert decide_res.status_code == 403


def test_coordinator_forbidden_from_admin_user_management_and_courses(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Coordinator receives 403 on all user management, password reset, and courses."""
    coord = create_test_user(real_db_session, "coord_guards@example.com", UserRole.COORDINATOR)
    target = create_test_user(real_db_session, "target_user@example.com", UserRole.STUDENT)

    login_test_user(real_db_client, coord.email)

    assert real_db_client.get("/api/admin/users").status_code == 403
    assert (
        real_db_client.post(
            "/api/admin/users",
            json={
                "email": "blocked@example.com",
                "password": "Password123!",
                "full_name": "Blocked",
                "role": "instructor",
            },
        ).status_code
        == 403
    )
    assert (
        real_db_client.patch(
            f"/api/admin/users/{target.id}",
            json={"is_active": False},
        ).status_code
        == 403
    )
    assert (
        real_db_client.put(
            f"/api/admin/users/{target.id}/password",
            json={"password": "NewPassword123!"},
        ).status_code
        == 403
    )

    # Course management
    assert real_db_client.post("/api/courses", json={"title": "Course"}).status_code == 403
    assert real_db_client.patch("/api/courses/1", json={"title": "Course"}).status_code == 403


def test_other_roles_forbidden_from_coordinator_endpoints(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Students, instructors, and organizations receive 403 on coordinator management endpoints."""
    roles = [UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORGANIZATION]
    for role in roles:
        user = create_test_user(real_db_session, f"block_{role.value}@example.com", role)
        login_test_user(real_db_client, user.email)

        assert real_db_client.get("/api/admin/organizations").status_code == 403
        assert real_db_client.get("/api/admin/internships").status_code == 403
        assert real_db_client.get("/api/dashboard/coordinator").status_code == 403
