"""Tests for student achievement badge isolation, application badges, and role guards."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import Application, ApplicationStatus
from app.models.internship import Internship, InternshipStatus, InternshipWorkMode
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_badge_internship_applications_boundary(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify first_application (0 vs 1) and offer_accepted (shortlisted vs accepted)."""
    student = create_test_user(real_db_session, "badge_app@example.com", UserRole.STUDENT)
    org = create_test_user(real_db_session, "badge_org@example.com", UserRole.ORGANIZATION)
    posting = Internship(
        organization_id=org.id,
        title="Web Intern",
        description="Full-stack",
        requirements="Python",
        location="Remote",
        work_mode=InternshipWorkMode.REMOTE,
        application_deadline=datetime.now(UTC) + timedelta(days=10),
        status=InternshipStatus.OPEN,
    )
    real_db_session.add(posting)
    real_db_session.commit()

    login_test_user(real_db_client, student.email)
    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["first_application"]["earned"] is False
    assert badges["first_application"]["progress"] == {"current": 0, "target": 1}
    assert badges["offer_accepted"]["earned"] is False
    assert badges["offer_accepted"]["progress"] == {"current": 0, "target": 1}

    # Submit application
    app = Application(
        posting_id=posting.id,
        student_id=student.id,
        cover_letter="Cover Letter",
        status=ApplicationStatus.SUBMITTED,
    )
    real_db_session.add(app)
    real_db_session.commit()

    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["first_application"]["earned"] is True
    assert badges["first_application"]["progress"] == {"current": 1, "target": 1}
    assert badges["offer_accepted"]["earned"] is False

    # Shortlist application -> offer_accepted still False
    app.status = ApplicationStatus.SHORTLISTED
    real_db_session.commit()

    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["offer_accepted"]["earned"] is False

    # Accept application -> offer_accepted earned
    app.status = ApplicationStatus.ACCEPTED
    real_db_session.commit()

    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["offer_accepted"]["earned"] is True
    assert badges["offer_accepted"]["progress"] == {"current": 1, "target": 1}


def test_badge_student_isolation(real_db_client: TestClient, real_db_session: Session) -> None:
    """Verify Student A's achievements never bleed into Student B's badge responses."""
    student_a = create_test_user(real_db_session, "iso_a@example.com", UserRole.STUDENT)
    student_b = create_test_user(real_db_session, "iso_b@example.com", UserRole.STUDENT)
    org = create_test_user(real_db_session, "iso_org@example.com", UserRole.ORGANIZATION)
    posting = Internship(
        organization_id=org.id,
        title="QA Intern",
        description="Testing",
        requirements="Pytest",
        location="Remote",
        work_mode=InternshipWorkMode.REMOTE,
        application_deadline=datetime.now(UTC) + timedelta(days=10),
        status=InternshipStatus.OPEN,
    )
    real_db_session.add(posting)
    real_db_session.commit()

    # Student A has an accepted application
    real_db_session.add(
        Application(
            posting_id=posting.id,
            student_id=student_a.id,
            cover_letter="Cover A",
            status=ApplicationStatus.ACCEPTED,
        )
    )
    real_db_session.commit()

    # Check student A has badges earned
    login_test_user(real_db_client, student_a.email)
    resp_a = real_db_client.get("/api/students/me/badges")
    badges_a = {b["id"]: b for b in resp_a.json()}
    assert badges_a["first_application"]["earned"] is True
    assert badges_a["offer_accepted"]["earned"] is True

    # Check student B has zero badges earned
    login_test_user(real_db_client, student_b.email)
    resp_b = real_db_client.get("/api/students/me/badges")
    badges_b = {b["id"]: b for b in resp_b.json()}
    assert badges_b["first_application"]["earned"] is False
    assert badges_b["offer_accepted"]["earned"] is False


def test_badge_role_and_auth_guards(real_db_client: TestClient, real_db_session: Session) -> None:
    """Verify badges endpoint requires authentication (401) and student role (403 for others)."""
    # Anonymous -> 401
    assert real_db_client.get("/api/students/me/badges").status_code == 401

    roles_to_block = [
        ("inst_b@example.com", UserRole.INSTRUCTOR),
        ("org_b@example.com", UserRole.ORGANIZATION),
        ("adm_b@example.com", UserRole.ADMIN),
        ("coord_b@example.com", UserRole.COORDINATOR),
    ]
    for email, role in roles_to_block:
        user = create_test_user(real_db_session, email, role)
        login_test_user(real_db_client, user.email)
        resp = real_db_client.get("/api/students/me/badges")
        assert resp.status_code == 403, f"Role {role.value} should receive 403"
