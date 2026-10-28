"""Integration tests for organization approval constraints on internship postings."""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from seed_demo import DEMO_PASSWORD, seed_demo

from app.models.internship import InternshipStatus
from app.models.organization_profile import ApprovalStatus
from app.models.user import UserRole
from tests.factories import (
    create_test_internship,
    create_test_organization,
    create_test_user,
    login_test_user,
)


def test_unapproved_organization_cannot_publish_internship(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Pending or rejected organizations cannot publish internships, but can create drafts."""
    org_user, profile = create_test_organization(
        real_db_session,
        email="pending_pub@test.com",
        organization_name="Pending Corp",
        approval_status=ApprovalStatus.PENDING,
    )

    login_test_user(real_db_client, org_user.email)

    # Creating draft is permitted
    deadline = (datetime.now(UTC) + timedelta(days=20)).isoformat()
    draft_resp = real_db_client.post(
        "/api/internships",
        json={
            "title": "Software Engineer Intern",
            "description": "Develop high-scale systems.",
            "requirements": "Python proficiency.",
            "location": "Nairobi",
            "work_mode": "remote",
            "duration_weeks": 12,
            "application_deadline": deadline,
        },
    )
    assert draft_resp.status_code == 201
    posting_id = draft_resp.json()["id"]

    # Submitting as pending organization gives 409 with exact message
    sub_resp = real_db_client.post(f"/api/internships/{posting_id}/submit")
    assert sub_resp.status_code == 409
    assert (
        sub_resp.json()["detail"]
        == "Your organization must be approved before you can submit internships"
    )
    assert sub_resp.json()["code"] == "ORGANIZATION_NOT_APPROVED"

    # Attempting to directly patch status to open gives 409
    patch_open_resp = real_db_client.patch(
        f"/api/internships/{posting_id}", json={"status": "open"}
    )
    assert patch_open_resp.status_code == 409
    assert patch_open_resp.json()["detail"] == "Submit for review instead"

    # Set status to rejected
    profile.approval_status = ApprovalStatus.REJECTED
    real_db_session.commit()

    rej_sub_resp = real_db_client.post(f"/api/internships/{posting_id}/submit")
    assert rej_sub_resp.status_code == 409
    assert (
        rej_sub_resp.json()["detail"]
        == "Your organization must be approved before you can submit internships"
    )

    # Once approved, organization can submit for review
    profile.approval_status = ApprovalStatus.APPROVED
    real_db_session.commit()

    approved_sub_resp = real_db_client.post(f"/api/internships/{posting_id}/submit")
    assert approved_sub_resp.status_code == 200
    assert approved_sub_resp.json()["status"] == "pending_review"


def test_catalogue_hides_unapproved_or_inactive_organization_postings(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Student catalogue and detail exclude postings whose organization
    is not approved or whose account is inactive.
    """
    approved_org, _ = create_test_organization(
        real_db_session,
        email="app_org@test.com",
        organization_name="Approved Org",
        approval_status=ApprovalStatus.APPROVED,
    )
    pending_org, _ = create_test_organization(
        real_db_session,
        email="pend_org@test.com",
        organization_name="Pending Org",
        approval_status=ApprovalStatus.PENDING,
    )
    inactive_org, _ = create_test_organization(
        real_db_session,
        email="inact_org@test.com",
        organization_name="Inactive Org",
        approval_status=ApprovalStatus.APPROVED,
    )
    inactive_org.is_active = False
    real_db_session.commit()

    post_approved = create_test_internship(
        real_db_session, approved_org, title="Approved Org Internship", status=InternshipStatus.OPEN
    )
    post_pending = create_test_internship(
        real_db_session, pending_org, title="Pending Org Internship", status=InternshipStatus.OPEN
    )
    post_inactive = create_test_internship(
        real_db_session, inactive_org, title="Inactive Org Internship", status=InternshipStatus.OPEN
    )

    student = create_test_user(real_db_session, email="student_cat@test.com", role=UserRole.STUDENT)
    login_test_user(real_db_client, student.email)

    # Student catalogue list
    cat_resp = real_db_client.get("/api/internships")
    assert cat_resp.status_code == 200
    cat_items = cat_resp.json()["items"]
    cat_ids = [i["id"] for i in cat_items]

    assert post_approved.id in cat_ids
    assert post_pending.id not in cat_ids
    assert post_inactive.id not in cat_ids

    # Student detail view
    assert real_db_client.get(f"/api/internships/{post_approved.id}").status_code == 200
    assert real_db_client.get(f"/api/internships/{post_pending.id}").status_code == 404
    assert real_db_client.get(f"/api/internships/{post_inactive.id}").status_code == 404

    # Admin view can see all
    admin = create_test_user(real_db_session, email="admin_inspector@test.com", role=UserRole.ADMIN)
    login_test_user(real_db_client, admin.email)
    admin_cat = real_db_client.get("/api/internships")
    assert admin_cat.status_code == 200
    admin_ids = [i["id"] for i in admin_cat.json()["items"]]
    assert post_approved.id in admin_ids
    assert post_pending.id in admin_ids
    assert post_inactive.id in admin_ids


def test_seeded_pending_organization_eyob_kassa_capabilities(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify exactly what pending demo organization Eyob Kassa can and cannot do."""
    seed_demo(real_db_session, force=True)

    # 1. Login succeeds
    login_test_user(real_db_client, "eyob.kassa@example.com", DEMO_PASSWORD)

    # 2. Can view dashboard and profile
    dash_resp = real_db_client.get("/api/dashboard/organization")
    assert dash_resp.status_code == 200
    assert dash_resp.json()["approval_status"] == "pending"

    prof_resp = real_db_client.get("/api/organizations/me")
    assert prof_resp.status_code == 200
    assert prof_resp.json()["approval_status"] == "pending"

    # 3. Can create draft internship posting
    deadline = (datetime.now(UTC) + timedelta(days=25)).isoformat()
    create_resp = real_db_client.post(
        "/api/internships",
        json={
            "title": "Data Engineering Intern",
            "description": "Build automated ETL pipelines.",
            "requirements": "SQL and Python skills.",
            "location": "Addis Ababa",
            "work_mode": "hybrid",
            "duration_weeks": 10,
            "application_deadline": deadline,
        },
    )
    assert create_resp.status_code == 201
    draft_data = create_resp.json()
    assert draft_data["status"] == "draft"
    posting_id = draft_data["id"]

    # 4. Can edit draft posting
    edit_resp = real_db_client.patch(
        f"/api/internships/{posting_id}",
        json={"title": "Data Engineering Intern 2026"},
    )
    assert edit_resp.status_code == 200
    assert edit_resp.json()["title"] == "Data Engineering Intern 2026"

    # 5. Cannot submit for review (returns 409 ORGANIZATION_NOT_APPROVED)
    sub_resp = real_db_client.post(f"/api/internships/{posting_id}/submit")
    assert sub_resp.status_code == 409
    assert sub_resp.json()["code"] == "ORGANIZATION_NOT_APPROVED"
    assert (
        sub_resp.json()["detail"]
        == "Your organization must be approved before you can submit internships"
    )

    # 6. Cannot publish directly (returns 409 SUBMIT_FOR_REVIEW_REQUIRED)
    pub_resp = real_db_client.patch(
        f"/api/internships/{posting_id}",
        json={"status": "open"},
    )
    assert pub_resp.status_code == 409
    assert pub_resp.json()["code"] == "SUBMIT_FOR_REVIEW_REQUIRED"
    assert pub_resp.json()["detail"] == "Submit for review instead"

    # 7. Draft is not visible to students in public catalogue
    real_db_client.post("/api/auth/logout")
    login_test_user(real_db_client, "abel.tesfaye@example.com", DEMO_PASSWORD)
    cat_resp = real_db_client.get("/api/internships")
    assert cat_resp.status_code == 200
    assert posting_id not in [i["id"] for i in cat_resp.json()["items"]]
    real_db_client.post("/api/auth/logout")
