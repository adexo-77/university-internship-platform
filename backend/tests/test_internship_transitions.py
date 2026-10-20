"""Tests for organization internship submission, withdrawal, closing, and edit locks."""

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


def test_submit_internship_owner_and_status_checks(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    owner, _ = create_test_organization(
        real_db_session, "owner_sub@test.com", approval_status=ApprovalStatus.APPROVED
    )
    other_org, _ = create_test_organization(
        real_db_session, "other_sub@test.com", approval_status=ApprovalStatus.APPROVED
    )
    student = create_test_user(real_db_session, "stud_sub@test.com", UserRole.STUDENT)

    posting = create_test_internship(real_db_session, owner, status=InternshipStatus.DRAFT)

    # Student forbidden
    login_test_user(real_db_client, student.email)
    assert real_db_client.post(f"/api/internships/{posting.id}/submit").status_code == 403

    # Other org gets 404
    login_test_user(real_db_client, other_org.email)
    assert real_db_client.post(f"/api/internships/{posting.id}/submit").status_code == 404

    # Owner submits successfully
    login_test_user(real_db_client, owner.email)
    resp = real_db_client.post(f"/api/internships/{posting.id}/submit")
    assert resp.status_code == 200
    assert resp.json()["status"] == "pending_review"

    # Cannot resubmit already pending_review posting
    assert real_db_client.post(f"/api/internships/{posting.id}/submit").status_code == 409


def test_withdraw_internship_checks(real_db_client: TestClient, real_db_session: Session) -> None:
    owner, _ = create_test_organization(
        real_db_session, "owner_with@test.com", approval_status=ApprovalStatus.APPROVED
    )
    other_org, _ = create_test_organization(
        real_db_session, "other_with@test.com", approval_status=ApprovalStatus.APPROVED
    )

    posting = create_test_internship(real_db_session, owner, status=InternshipStatus.PENDING_REVIEW)

    # Other org gets 404
    login_test_user(real_db_client, other_org.email)
    assert real_db_client.post(f"/api/internships/{posting.id}/withdraw").status_code == 404

    # Owner withdraws to draft
    login_test_user(real_db_client, owner.email)
    resp = real_db_client.post(f"/api/internships/{posting.id}/withdraw")
    assert resp.status_code == 200
    assert resp.json()["status"] == "draft"

    # Cannot withdraw when already in draft
    assert real_db_client.post(f"/api/internships/{posting.id}/withdraw").status_code == 409


def test_close_internship_checks(real_db_client: TestClient, real_db_session: Session) -> None:
    owner, _ = create_test_organization(
        real_db_session, "owner_cls@test.com", approval_status=ApprovalStatus.APPROVED
    )
    other_org, _ = create_test_organization(
        real_db_session, "other_cls@test.com", approval_status=ApprovalStatus.APPROVED
    )

    open_posting = create_test_internship(real_db_session, owner, status=InternshipStatus.OPEN)

    # Other org gets 404
    login_test_user(real_db_client, other_org.email)
    assert real_db_client.post(f"/api/internships/{open_posting.id}/close").status_code == 404

    # Owner closes posting
    login_test_user(real_db_client, owner.email)
    resp = real_db_client.post(f"/api/internships/{open_posting.id}/close")
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"

    # Cannot close already closed posting
    assert real_db_client.post(f"/api/internships/{open_posting.id}/close").status_code == 409


def test_open_posting_deadline_extension_and_locks(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    owner, _ = create_test_organization(
        real_db_session, "owner_ext@test.com", approval_status=ApprovalStatus.APPROVED
    )
    base_deadline = datetime.now(UTC) + timedelta(days=15)
    posting = create_test_internship(
        real_db_session,
        owner,
        status=InternshipStatus.OPEN,
        application_deadline=base_deadline,
    )
    login_test_user(real_db_client, owner.email)

    # Attempting to edit content on open posting gives 409
    content_resp = real_db_client.patch(
        f"/api/internships/{posting.id}",
        json={"title": "Brand New Title"},
    )
    assert content_resp.status_code == 409
    assert (
        content_resp.json()["detail"]
        == "Cannot edit content of an open posting; only deadline extension is allowed"
    )

    # Shortening deadline gives 409
    earlier_deadline = (base_deadline - timedelta(days=5)).isoformat()
    shorten_resp = real_db_client.patch(
        f"/api/internships/{posting.id}",
        json={"application_deadline": earlier_deadline},
    )
    assert shorten_resp.status_code == 409
    assert (
        shorten_resp.json()["detail"] == "Application deadline can only be extended, not shortened"
    )

    # Extending deadline succeeds
    later_deadline = (base_deadline + timedelta(days=10)).isoformat()
    extend_resp = real_db_client.patch(
        f"/api/internships/{posting.id}",
        json={"application_deadline": later_deadline},
    )
    assert extend_resp.status_code == 200


def test_pending_review_posting_locked(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    owner, _ = create_test_organization(
        real_db_session, "owner_lck@test.com", approval_status=ApprovalStatus.APPROVED
    )
    posting = create_test_internship(real_db_session, owner, status=InternshipStatus.PENDING_REVIEW)
    login_test_user(real_db_client, owner.email)

    resp = real_db_client.patch(
        f"/api/internships/{posting.id}",
        json={"title": "Change Title"},
    )
    assert resp.status_code == 409
    assert (
        resp.json()["detail"]
        == "Posting is pending review and cannot be edited. Withdraw to draft to edit."
    )
