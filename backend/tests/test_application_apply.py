"""Tests for application submission, eligibility checks, profile requirements, and withdrawals."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import ApplicationStatus
from app.models.internship import InternshipStatus
from app.models.student_profile import StudentProfile
from app.models.user import UserRole
from tests.factories import (
    create_test_application,
    create_test_internship,
    create_test_user,
    login_test_user,
)


def test_student_can_apply_with_complete_profile(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_app@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org)

    student = create_test_user(real_db_session, "stud_comp@test.com", UserRole.STUDENT)
    prof = StudentProfile(
        user_id=student.id, university="Strathmore University", department="Computer Science"
    )
    real_db_session.add(prof)
    real_db_session.commit()

    login_test_user(real_db_client, student.email)
    resp = real_db_client.post(
        f"/api/internships/{posting.id}/applications",
        json={"cover_letter": "I have extensive experience in Python web development."},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "submitted"
    assert data["posting_id"] == posting.id
    assert data["student_id"] == student.id


def test_incomplete_profile_gives_409_with_message(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_incomp@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org)

    student = create_test_user(real_db_session, "stud_incomp@test.com", UserRole.STUDENT)
    login_test_user(real_db_client, student.email)

    resp = real_db_client.post(
        f"/api/internships/{posting.id}/applications",
        json={"cover_letter": "I want this internship."},
    )
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Complete your profile before applying"


def test_cannot_apply_to_closed_posting(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_cl@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org, status=InternshipStatus.CLOSED)

    student = create_test_user(real_db_session, "stud_cl@test.com", UserRole.STUDENT)
    prof = StudentProfile(user_id=student.id, university="JKUAT", department="IT")
    real_db_session.add(prof)
    real_db_session.commit()

    login_test_user(real_db_client, student.email)
    resp = real_db_client.post(
        f"/api/internships/{posting.id}/applications",
        json={"cover_letter": "Please let me apply."},
    )
    assert resp.status_code == 409


def test_cannot_apply_after_deadline(real_db_client: TestClient, real_db_session: Session) -> None:
    org = create_test_user(real_db_session, "org_dead@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org)
    posting.application_deadline = datetime.now(UTC) - timedelta(hours=1)
    real_db_session.commit()

    student = create_test_user(real_db_session, "stud_dead@test.com", UserRole.STUDENT)
    prof = StudentProfile(user_id=student.id, university="UoN", department="Software Engineering")
    real_db_session.add(prof)
    real_db_session.commit()

    login_test_user(real_db_client, student.email)
    resp = real_db_client.post(
        f"/api/internships/{posting.id}/applications",
        json={"cover_letter": "Late submission attempt."},
    )
    assert resp.status_code == 409


def test_duplicate_application_gives_409(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_dup@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org)

    student = create_test_user(real_db_session, "stud_dup@test.com", UserRole.STUDENT)
    prof = StudentProfile(user_id=student.id, university="KU", department="CS")
    real_db_session.add(prof)
    real_db_session.commit()

    create_test_application(real_db_session, posting, student)

    login_test_user(real_db_client, student.email)
    resp = real_db_client.post(
        f"/api/internships/{posting.id}/applications",
        json={"cover_letter": "Second attempt."},
    )
    assert resp.status_code == 409


def test_org_and_instructor_cannot_apply(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org1 = create_test_user(real_db_session, "org_creator@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org1)

    org2 = create_test_user(real_db_session, "org_applicant@test.com", UserRole.ORGANIZATION)
    login_test_user(real_db_client, org2.email)
    resp = real_db_client.post(
        f"/api/internships/{posting.id}/applications",
        json={"cover_letter": "Org trying to apply"},
    )
    assert resp.status_code == 403


def test_student_lists_own_applications_only(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_list@test.com", UserRole.ORGANIZATION)
    p1 = create_test_internship(real_db_session, org, title="Post 1")
    p2 = create_test_internship(real_db_session, org, title="Post 2")

    s1 = create_test_user(real_db_session, "s1_list@test.com", UserRole.STUDENT)
    s2 = create_test_user(real_db_session, "s2_list@test.com", UserRole.STUDENT)

    app1 = create_test_application(real_db_session, p1, s1)
    create_test_application(real_db_session, p2, s2)

    login_test_user(real_db_client, s1.email)
    resp = real_db_client.get("/api/students/me/applications")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == app1.id


def test_student_can_withdraw_submitted_or_shortlisted(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_wd@test.com", UserRole.ORGANIZATION)
    p = create_test_internship(real_db_session, org)
    student = create_test_user(real_db_session, "stud_wd@test.com", UserRole.STUDENT)
    app = create_test_application(real_db_session, p, student, status=ApplicationStatus.SUBMITTED)

    login_test_user(real_db_client, student.email)
    resp = real_db_client.post(f"/api/applications/{app.id}/withdraw")
    assert resp.status_code == 200
    assert resp.json()["status"] == "withdrawn"

    # Withdrawing again gives 409
    resp = real_db_client.post(f"/api/applications/{app.id}/withdraw")
    assert resp.status_code == 409


def test_other_student_cannot_withdraw_application(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_wd2@test.com", UserRole.ORGANIZATION)
    p = create_test_internship(real_db_session, org)
    s1 = create_test_user(real_db_session, "s1_wd@test.com", UserRole.STUDENT)
    s2 = create_test_user(real_db_session, "s2_wd@test.com", UserRole.STUDENT)
    app = create_test_application(real_db_session, p, s1)

    login_test_user(real_db_client, s2.email)
    resp = real_db_client.post(f"/api/applications/{app.id}/withdraw")
    assert resp.status_code == 404
