"""Tests for internship posting creation, ownership, and management workflows."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.internship import InternshipStatus
from app.models.user import UserRole
from tests.factories import (
    create_test_application,
    create_test_internship,
    create_test_user,
    login_test_user,
)


def test_org_can_create_internship_posting(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "tech@corp.org", UserRole.ORGANIZATION)
    login_test_user(real_db_client, org.email)

    deadline = (datetime.now(UTC) + timedelta(days=30)).isoformat()
    resp = real_db_client.post(
        "/api/internships",
        json={
            "title": "Backend Engineering Intern",
            "description": "Work on distributed systems and APIs.",
            "requirements": "Python, SQL, Linux fundamentals.",
            "location": "Nairobi / Remote",
            "work_mode": "hybrid",
            "duration_weeks": 12,
            "application_deadline": deadline,
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Backend Engineering Intern"
    assert data["status"] == "draft"
    assert data["work_mode"] == "hybrid"
    assert data["organization_id"] == org.id

    # Extra fields like status or organization_id are forbidden
    extra_resp = real_db_client.post(
        "/api/internships",
        json={
            "title": "Backend Engineering Intern",
            "description": "Work on distributed systems and APIs.",
            "requirements": "Python, SQL, Linux fundamentals.",
            "location": "Nairobi / Remote",
            "work_mode": "hybrid",
            "application_deadline": deadline,
            "status": "open",
        },
    )
    assert extra_resp.status_code == 422


def test_create_internship_requires_future_deadline(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "future@corp.org", UserRole.ORGANIZATION)
    login_test_user(real_db_client, org.email)

    past_deadline = (datetime.now(UTC) - timedelta(days=1)).isoformat()
    resp = real_db_client.post(
        "/api/internships",
        json={
            "title": "Old Intern",
            "description": "Past deadline test.",
            "requirements": "None",
            "location": "Remote",
            "work_mode": "remote",
            "application_deadline": past_deadline,
        },
    )
    assert resp.status_code == 422


def test_student_and_instructor_cannot_create_internship(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    student = create_test_user(real_db_session, "student@univ.edu", UserRole.STUDENT)
    login_test_user(real_db_client, student.email)

    deadline = (datetime.now(UTC) + timedelta(days=10)).isoformat()
    resp = real_db_client.post(
        "/api/internships",
        json={
            "title": "Unauthorized Posting",
            "description": "Should fail.",
            "requirements": "None",
            "location": "Remote",
            "work_mode": "remote",
            "application_deadline": deadline,
        },
    )
    assert resp.status_code == 403


def test_org_lists_own_postings_with_applicant_count(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org1 = create_test_user(real_db_session, "org1@test.com", UserRole.ORGANIZATION)
    org2 = create_test_user(real_db_session, "org2@test.com", UserRole.ORGANIZATION)
    posting1 = create_test_internship(real_db_session, org1, title="Posting 1")
    posting2 = create_test_internship(real_db_session, org1, title="Posting 2")
    create_test_internship(real_db_session, org2, title="Posting Org 2")

    student = create_test_user(real_db_session, "app_student@test.com", UserRole.STUDENT)
    create_test_application(real_db_session, posting1, student)

    login_test_user(real_db_client, org1.email)
    resp = real_db_client.get("/api/organizations/me/internships")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    p1 = next(item for item in data if item["id"] == posting1.id)
    p2 = next(item for item in data if item["id"] == posting2.id)
    assert p1["applicant_count"] == 1
    assert p2["applicant_count"] == 0


def test_org_can_update_draft_or_open_posting(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "updater@corp.org", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org, status=InternshipStatus.DRAFT)
    login_test_user(real_db_client, org.email)

    resp = real_db_client.patch(
        f"/api/internships/{posting.id}",
        json={"title": "Updated Title", "duration_weeks": 16},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"
    assert resp.json()["duration_weeks"] == 16


def test_internship_status_transition_rules(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org = create_test_user(real_db_session, "status@corp.org", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org, status=InternshipStatus.OPEN)
    login_test_user(real_db_client, org.email)

    # moving draft directly to open via patch returns 409
    draft_posting = create_test_internship(
        real_db_session, org, title="Draft Post", status=InternshipStatus.DRAFT
    )
    direct_open_resp = real_db_client.patch(
        f"/api/internships/{draft_posting.id}", json={"status": "open"}
    )
    assert direct_open_resp.status_code == 409
    assert direct_open_resp.json()["detail"] == "Submit for review instead"

    # open -> closed
    resp = real_db_client.patch(f"/api/internships/{posting.id}", json={"status": "closed"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"

    # closed is final; reopening must fail (409)
    resp = real_db_client.patch(f"/api/internships/{posting.id}", json={"status": "open"})
    assert resp.status_code == 409

    # closed posting cannot be edited at all (409)
    resp = real_db_client.patch(f"/api/internships/{posting.id}", json={"title": "Change Title"})
    assert resp.status_code == 409


def test_other_org_cannot_edit_posting(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    org1 = create_test_user(real_db_session, "owner@org.com", UserRole.ORGANIZATION)
    org2 = create_test_user(real_db_session, "stranger@org.com", UserRole.ORGANIZATION)
    posting = create_test_internship(real_db_session, org1)

    login_test_user(real_db_client, org2.email)
    resp = real_db_client.patch(f"/api/internships/{posting.id}", json={"title": "Hacked"})
    assert resp.status_code == 404
