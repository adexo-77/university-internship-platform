"""Integration tests for the organization dashboard endpoint."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import ApplicationStatus
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


def test_organization_dashboard_role_guards(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Only authenticated organizations may access the organization dashboard."""
    real_db_client.cookies.clear()
    assert real_db_client.get("/api/dashboard/organization").status_code == 401

    for role in [UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ADMIN]:
        u = create_test_user(real_db_session, f"org_guard_{role.value}@test.com", role)
        login_test_user(real_db_client, u.email)
        assert real_db_client.get("/api/dashboard/organization").status_code == 403

    org_user, _ = create_test_organization(real_db_session, "org_guard_ok@test.com")
    login_test_user(real_db_client, org_user.email)
    assert real_db_client.get("/api/dashboard/organization").status_code == 200


def test_organization_dashboard_empty_state(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Empty organization account returns default status, zero counts, and empty applications."""
    org_user = create_test_user(real_db_session, "org_empty@test.com", UserRole.ORGANIZATION)
    login_test_user(real_db_client, org_user.email)

    resp = real_db_client.get("/api/dashboard/organization")
    assert resp.status_code == 200
    data = resp.json()

    assert data["approval_status"] == "pending"
    assert data["approval_note"] is None
    assert data["applications_awaiting_decision"] == 0
    assert data["recent_applications"] == []
    assert data["postings"]["total"] == 0
    for count in data["postings"]["counts_by_status"].values():
        assert count == 0


def test_organization_dashboard_metrics_and_isolation(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Organization dashboard aggregates posting counts, awaiting apps, and isolates orgs."""
    org_a, prof_a = create_test_organization(
        real_db_session,
        "org_met_a@test.com",
        organization_name="Alpha Tech",
        approval_status=ApprovalStatus.APPROVED,
    )
    prof_a.approval_note = "Identity verified."
    real_db_session.commit()

    org_b, _ = create_test_organization(
        real_db_session,
        "org_met_b@test.com",
        organization_name="Beta Corp",
        approval_status=ApprovalStatus.APPROVED,
    )

    student_1, _ = create_test_student(real_db_session, "org_stud_1@test.com")
    student_2, _ = create_test_student(real_db_session, "org_stud_2@test.com")

    # Org A postings
    p1 = create_test_internship(
        real_db_session, org_a, title="Alpha Post 1", status=InternshipStatus.OPEN
    )
    create_test_internship(
        real_db_session, org_a, title="Alpha Post 2", status=InternshipStatus.DRAFT
    )
    create_test_internship(
        real_db_session, org_a, title="Alpha Post 3", status=InternshipStatus.PENDING_REVIEW
    )

    # Org B posting (isolation test)
    p_b = create_test_internship(
        real_db_session, org_b, title="Beta Post", status=InternshipStatus.OPEN
    )

    # Applications for Org A
    now = datetime.now(UTC)
    app1 = create_test_application(
        real_db_session, p1, student_1, status=ApplicationStatus.SUBMITTED
    )
    app2 = create_test_application(
        real_db_session, p1, student_2, status=ApplicationStatus.ACCEPTED
    )

    # Application for Org B
    create_test_application(real_db_session, p_b, student_1, status=ApplicationStatus.SUBMITTED)

    # Set created dates for ordering test
    app1.created_at = now - timedelta(hours=2)
    app2.created_at = now - timedelta(hours=1)
    real_db_session.commit()

    login_test_user(real_db_client, org_a.email)
    resp = real_db_client.get("/api/dashboard/organization")
    assert resp.status_code == 200
    data = resp.json()

    # Approval
    assert data["approval_status"] == "approved"
    assert data["approval_note"] == "Identity verified."

    # Postings summary
    assert data["postings"]["total"] == 3
    assert data["postings"]["counts_by_status"]["open"] == 1
    assert data["postings"]["counts_by_status"]["draft"] == 1
    assert data["postings"]["counts_by_status"]["pending_review"] == 1
    assert data["postings"]["counts_by_status"]["closed"] == 0

    # Applications awaiting decision: only app1 is submitted
    assert data["applications_awaiting_decision"] == 1

    # 5 latest applications: ordered latest first (app2 then app1)
    recent = data["recent_applications"]
    assert len(recent) == 2
    assert recent[0]["application_id"] == app2.id
    assert recent[0]["status"] == "accepted"
    assert recent[1]["application_id"] == app1.id
    assert recent[1]["status"] == "submitted"
