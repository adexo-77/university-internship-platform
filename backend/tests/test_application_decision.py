"""Tests for applicant roster visibility, detail access, and organization decision workflows."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import ApplicationStatus
from app.models.student_profile import StudentProfile
from app.models.user import UserRole
from tests.factories import (
    create_test_application,
    create_test_internship,
    create_test_user,
    login_test_user,
)


def test_org_views_applicant_roster_with_profiles(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_roster@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org)

    student = create_test_user(
        real_db_session, "applicant_joe@test.com", UserRole.STUDENT, full_name="Joe Doe"
    )
    prof = StudentProfile(
        user_id=student.id,
        university="Technical University",
        department="Computer Systems",
        year_of_study=3,
        skills=["Python", "FastAPI"],
        bio="Aspiring systems engineer.",
    )
    real_db_session.add(prof)
    real_db_session.commit()

    create_test_application(
        real_db_session, posting, student, cover_letter="My application letter."
    )

    login_test_user(real_db_client, org.email)
    resp = real_db_client.get(f"/api/internships/{posting.id}/applications")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    app_data = data[0]
    assert app_data["applicant"] is not None
    assert app_data["applicant"]["full_name"] == "Joe Doe"
    assert app_data["applicant"]["university"] == "Technical University"
    assert app_data["applicant"]["skills"] == ["Python", "FastAPI"]
    assert app_data["cover_letter"] == "My application letter."


def test_admin_views_roster_but_other_org_gets_404(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org1 = create_test_user(real_db_session, "owner_rost@test.com", UserRole.ORGANIZATION)
    org2 = create_test_user(real_db_session, "stranger_rost@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org1)

    student = create_test_user(real_db_session, "stud_rost@test.com", UserRole.STUDENT)
    create_test_application(real_db_session, posting, student)

    # Other org gets 404
    login_test_user(real_db_client, org2.email)
    assert real_db_client.get(f"/api/internships/{posting.id}/applications").status_code == 404

    # Admin gets 200
    admin = create_test_user(real_db_session, "admin_rost@test.com", UserRole.ADMIN)
    login_test_user(real_db_client, admin.email)
    assert real_db_client.get(f"/api/internships/{posting.id}/applications").status_code == 200


def test_application_detail_access_permissions(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_acc@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org)
    student = create_test_user(real_db_session, "stud_acc@test.com", UserRole.STUDENT)
    app = create_test_application(real_db_session, posting, student)

    other_student = create_test_user(real_db_session, "other_acc@test.com", UserRole.STUDENT)
    admin = create_test_user(real_db_session, "admin_acc@test.com", UserRole.ADMIN)

    # Student owner sees it
    login_test_user(real_db_client, student.email)
    assert real_db_client.get(f"/api/applications/{app.id}").status_code == 200

    # Org owner sees it
    login_test_user(real_db_client, org.email)
    assert real_db_client.get(f"/api/applications/{app.id}").status_code == 200

    # Admin sees it
    login_test_user(real_db_client, admin.email)
    assert real_db_client.get(f"/api/applications/{app.id}").status_code == 200

    # Other student gets 404
    login_test_user(real_db_client, other_student.email)
    assert real_db_client.get(f"/api/applications/{app.id}").status_code == 404


def test_org_decision_state_machine_and_finality(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "org_decide@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org)
    student = create_test_user(real_db_session, "stud_decide@test.com", UserRole.STUDENT)
    app = create_test_application(real_db_session, posting, student)

    login_test_user(real_db_client, org.email)

    # submitted -> shortlisted
    resp = real_db_client.put(
        f"/api/applications/{app.id}/decision",
        json={"status": "shortlisted", "decision_message": "Strong profile."},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "shortlisted"

    # shortlisted -> accepted
    resp = real_db_client.put(
        f"/api/applications/{app.id}/decision",
        json={"status": "accepted", "decision_message": "Welcome aboard!"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"
    assert resp.json()["decided_at"] is not None

    # accepted is final -> 409
    resp = real_db_client.put(
        f"/api/applications/{app.id}/decision",
        json={"status": "rejected", "decision_message": "Change mind."},
    )
    assert resp.status_code == 409


def test_withdrawn_cannot_be_decided(real_db_client: TestClient, real_db_session: Session) -> None:
    org = create_test_user(real_db_session, "org_wd_dec@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org)
    student = create_test_user(real_db_session, "stud_wd_dec@test.com", UserRole.STUDENT)
    app = create_test_application(
        real_db_session, posting, student, status=ApplicationStatus.WITHDRAWN
    )

    login_test_user(real_db_client, org.email)
    resp = real_db_client.put(
        f"/api/applications/{app.id}/decision",
        json={"status": "shortlisted"},
    )
    assert resp.status_code == 409


def test_admin_and_other_org_cannot_decide(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org1 = create_test_user(real_db_session, "org_main@test.com", UserRole.ORGANIZATION)
    org2 = create_test_user(real_db_session, "org_other@test.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org1)
    student = create_test_user(real_db_session, "stud_unauth@test.com", UserRole.STUDENT)
    app = create_test_application(real_db_session, posting, student)

    # Admin is read-only -> 403
    admin = create_test_user(real_db_session, "admin_dec@test.com", UserRole.ADMIN)
    login_test_user(real_db_client, admin.email)
    resp = real_db_client.put(f"/api/applications/{app.id}/decision", json={"status": "accepted"})
    assert resp.status_code == 403

    # Other org gets 404
    login_test_user(real_db_client, org2.email)
    resp = real_db_client.put(f"/api/applications/{app.id}/decision", json={"status": "accepted"})
    assert resp.status_code == 404
