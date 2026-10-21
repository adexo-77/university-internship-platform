"""Integration tests for administrator review, rejection, takedown, and privacy."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

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


def test_admin_internship_review_queue(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    admin = create_test_user(real_db_session, "adm_queue@test.com", UserRole.ADMIN)
    org, _ = create_test_organization(
        real_db_session, "org_queue@test.com", approval_status=ApprovalStatus.APPROVED
    )

    now = datetime.now(UTC)
    p1 = create_test_internship(
        real_db_session,
        org,
        title="Earlier Post",
        status=InternshipStatus.PENDING_REVIEW,
        created_at=now - timedelta(days=2),
    )
    p2 = create_test_internship(
        real_db_session,
        org,
        title="Later Post",
        status=InternshipStatus.PENDING_REVIEW,
        created_at=now - timedelta(days=1),
    )
    p_open = create_test_internship(
        real_db_session, org, title="Open Post", status=InternshipStatus.OPEN
    )

    login_test_user(real_db_client, admin.email)
    resp = real_db_client.get("/api/admin/internships")
    assert resp.status_code == 200
    ids = [item["id"] for item in resp.json()["items"]]
    assert ids.index(p1.id) < ids.index(p2.id)
    assert p_open.id not in ids


def test_admin_internships_status_filters_and_role_guards(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    admin = create_test_user(real_db_session, "adm_flt@test.com", UserRole.ADMIN)
    student = create_test_user(real_db_session, "stud_flt@test.com", UserRole.STUDENT)
    instructor = create_test_user(real_db_session, "inst_flt@test.com", UserRole.INSTRUCTOR)
    org, _ = create_test_organization(
        real_db_session, "org_flt@test.com", approval_status=ApprovalStatus.APPROVED
    )

    p_pending = create_test_internship(real_db_session, org, status=InternshipStatus.PENDING_REVIEW)
    p_open = create_test_internship(real_db_session, org, status=InternshipStatus.OPEN)

    for role_user in (student, instructor, org):
        login_test_user(real_db_client, role_user.email)
        assert real_db_client.get("/api/admin/internships").status_code == 403
        assert real_db_client.get("/api/admin/internships?status=open").status_code == 403
        assert real_db_client.get("/api/admin/internships?status=all").status_code == 403

    login_test_user(real_db_client, admin.email)
    resp_open = real_db_client.get("/api/admin/internships?status=open")
    assert resp_open.status_code == 200
    open_ids = [i["id"] for i in resp_open.json()["items"]]
    assert p_open.id in open_ids and p_pending.id not in open_ids

    resp_all = real_db_client.get("/api/admin/internships?status=all")
    assert resp_all.status_code == 200
    all_ids = [i["id"] for i in resp_all.json()["items"]]
    assert p_open.id in all_ids and p_pending.id in all_ids


def test_admin_approve_and_reject_transitions(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    admin = create_test_user(real_db_session, "adm_dec@test.com", UserRole.ADMIN)
    org, _ = create_test_organization(
        real_db_session, "org_dec@test.com", approval_status=ApprovalStatus.APPROVED
    )
    p_app = create_test_internship(real_db_session, org, status=InternshipStatus.PENDING_REVIEW)
    p_rej = create_test_internship(real_db_session, org, status=InternshipStatus.PENDING_REVIEW)

    login_test_user(real_db_client, admin.email)

    # Approve
    resp_app = real_db_client.put(
        f"/api/admin/internships/{p_app.id}/review", json={"decision": "approved"}
    )
    assert resp_app.status_code == 200
    data_app = resp_app.json()
    assert data_app["status"] == "open"
    assert data_app["reviewed_by"] == admin.id
    assert data_app["reviewed_at"] is not None

    # Rejection requires note (422)
    resp_no_note = real_db_client.put(
        f"/api/admin/internships/{p_rej.id}/review", json={"decision": "rejected"}
    )
    assert resp_no_note.status_code == 422

    # Reject with note
    resp_rej = real_db_client.put(
        f"/api/admin/internships/{p_rej.id}/review",
        json={"decision": "rejected", "review_note": "Unclear compensation and scope."},
    )
    assert resp_rej.status_code == 200
    data_rej = resp_rej.json()
    assert data_rej["status"] == "rejected"
    assert data_rej["review_note"] == "Unclear compensation and scope."


def test_admin_takedown_and_catalog_and_application_effects(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    admin = create_test_user(real_db_session, "adm_tkd@test.com", UserRole.ADMIN)
    org, _ = create_test_organization(
        real_db_session, "org_tkd@test.com", approval_status=ApprovalStatus.APPROVED
    )
    student_user, _ = create_test_student(real_db_session, "stud_tkd@test.com")

    posting = create_test_internship(real_db_session, org, status=InternshipStatus.OPEN)
    create_test_application(real_db_session, posting, student_user)

    # Non-admin forbidden (403)
    login_test_user(real_db_client, student_user.email)
    forbidden_resp = real_db_client.put(
        f"/api/admin/internships/{posting.id}/review",
        json={"decision": "rejected", "review_note": "Violated terms."},
    )
    assert forbidden_resp.status_code == 403

    # Admin takedown without note gives 422
    login_test_user(real_db_client, admin.email)
    resp_missing_note = real_db_client.put(
        f"/api/admin/internships/{posting.id}/review", json={"decision": "rejected"}
    )
    assert resp_missing_note.status_code == 422

    # Admin takes down open posting with note (200, status=rejected, reviewed_by & reviewed_at set)
    resp_tkd = real_db_client.put(
        f"/api/admin/internships/{posting.id}/review",
        json={"decision": "rejected", "review_note": "Violated terms."},
    )
    assert resp_tkd.status_code == 200
    data_tkd = resp_tkd.json()
    assert data_tkd["status"] == "rejected"
    assert data_tkd["reviewed_by"] == admin.id
    assert data_tkd["reviewed_at"] is not None

    # Student cannot see taken-down posting in catalog
    login_test_user(real_db_client, student_user.email)
    cat_resp = real_db_client.get("/api/internships")
    assert cat_resp.status_code == 200
    ids = [i["id"] for i in cat_resp.json()["items"]]
    assert posting.id not in ids

    # Student detail view returns 404
    assert real_db_client.get(f"/api/internships/{posting.id}").status_code == 404

    # New application blocked (409)
    other_student, _ = create_test_student(real_db_session, "other_tkd@test.com")
    login_test_user(real_db_client, other_student.email)
    app_resp = real_db_client.post(
        f"/api/internships/{posting.id}/applications",
        json={"cover_letter": "I want to apply."},
    )
    assert app_resp.status_code == 409

    # Existing applications remain visible to student
    login_test_user(real_db_client, student_user.email)
    my_apps = real_db_client.get("/api/students/me/applications").json()
    assert any(a["posting_id"] == posting.id for a in my_apps)

    # Existing applications remain visible to organization
    login_test_user(real_db_client, org.email)
    org_apps = real_db_client.get(f"/api/internships/{posting.id}/applications").json()
    assert len(org_apps) == 1


def test_resubmission_after_rejection_and_review_note_privacy(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    admin = create_test_user(real_db_session, "adm_priv@test.com", UserRole.ADMIN)
    org, _ = create_test_organization(
        real_db_session, "org_priv@test.com", approval_status=ApprovalStatus.APPROVED
    )
    other_org, _ = create_test_organization(
        real_db_session, "stranger_priv@test.com", approval_status=ApprovalStatus.APPROVED
    )

    posting = create_test_internship(
        real_db_session,
        org,
        status=InternshipStatus.REJECTED,
        review_note="Fix requirements.",
    )

    # Owner can edit content of rejected posting
    login_test_user(real_db_client, org.email)
    edit_resp = real_db_client.patch(
        f"/api/internships/{posting.id}",
        json={"title": "Better Title", "requirements": "Fixed requirements."},
    )
    assert edit_resp.status_code == 200
    assert edit_resp.json()["title"] == "Better Title"

    # Owner sees review note
    assert edit_resp.json()["review_note"] == "Fix requirements."

    # Admin sees review note
    login_test_user(real_db_client, admin.email)
    admin_detail = real_db_client.get(f"/api/internships/{posting.id}").json()
    assert admin_detail["review_note"] == "Fix requirements."

    # Other org cannot see posting
    login_test_user(real_db_client, other_org.email)
    assert real_db_client.get(f"/api/internships/{posting.id}").status_code == 404

    # Owner resubmits after edits
    login_test_user(real_db_client, org.email)
    resub_resp = real_db_client.post(f"/api/internships/{posting.id}/submit")
    assert resub_resp.status_code == 200
    assert resub_resp.json()["status"] == "pending_review"
