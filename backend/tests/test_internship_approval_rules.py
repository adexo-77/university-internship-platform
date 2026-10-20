"""Integration tests for organization approval constraints on internship postings."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

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

    # Publishing as pending organization gives 409 with exact message
    pub_resp = real_db_client.patch(f"/api/internships/{posting_id}", json={"status": "open"})
    assert pub_resp.status_code == 409
    assert (
        pub_resp.json()["detail"]
        == "Your organization must be approved before you can publish internships"
    )
    assert pub_resp.json()["code"] == "ORGANIZATION_NOT_APPROVED"

    # Set status to rejected
    profile.approval_status = ApprovalStatus.REJECTED
    real_db_session.commit()

    rej_pub_resp = real_db_client.patch(f"/api/internships/{posting_id}", json={"status": "open"})
    assert rej_pub_resp.status_code == 409
    assert (
        rej_pub_resp.json()["detail"]
        == "Your organization must be approved before you can publish internships"
    )

    # Once approved, organization can publish
    profile.approval_status = ApprovalStatus.APPROVED
    real_db_session.commit()

    approved_pub_resp = real_db_client.patch(
        f"/api/internships/{posting_id}", json={"status": "open"}
    )
    assert approved_pub_resp.status_code == 200
    assert approved_pub_resp.json()["status"] == "open"


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
