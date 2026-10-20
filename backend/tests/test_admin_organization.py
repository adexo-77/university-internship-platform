"""Integration tests for administrator organization review and approval workflow."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.organization_profile import ApprovalStatus
from app.models.user import UserRole
from tests.factories import create_test_organization, create_test_user, login_test_user


def test_admin_organization_endpoints_role_guards(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Admin organization endpoints return 401 when signed out and 403 for non-admins."""
    org_user, _ = create_test_organization(real_db_session, email="org_guards@test.com")

    endpoints = [
        ("GET", "/api/admin/organizations", None),
        (
            "PUT",
            f"/api/admin/organizations/{org_user.id}/approval",
            {"approval_status": "approved"},
        ),
    ]

    for method, url, payload in endpoints:
        real_db_client.cookies.clear()
        resp = real_db_client.request(method, url, json=payload)
        assert resp.status_code == 401, f"{method} {url} should be 401 signed out"

    for role in [UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORGANIZATION]:
        user = create_test_user(real_db_session, email=f"user_org_{role.value}@test.com", role=role)
        login_test_user(real_db_client, user.email)
        for method, url, payload in endpoints:
            resp = real_db_client.request(method, url, json=payload)
            assert resp.status_code == 403, f"{method} {url} should be 403 for {role.value}"


def test_admin_list_organizations_filter_and_fields(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Admin can list organizations and filter by approval status with required fields."""
    admin = create_test_user(real_db_session, email="admin_org_list@test.com", role=UserRole.ADMIN)
    create_test_organization(
        real_db_session,
        email="pending_org@test.com",
        organization_name="Pending Inc",
        approval_status=ApprovalStatus.PENDING,
    )
    create_test_organization(
        real_db_session,
        email="approved_org@test.com",
        organization_name="Approved Corp",
        approval_status=ApprovalStatus.APPROVED,
    )

    login_test_user(real_db_client, admin.email)

    resp = real_db_client.get("/api/admin/organizations")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data and "total" in data

    # Filter by pending
    resp_pending = real_db_client.get("/api/admin/organizations?approval_status=pending")
    assert resp_pending.status_code == 200
    pending_items = resp_pending.json()["items"]
    assert any(i["organization_name"] == "Pending Inc" for i in pending_items)
    assert not any(i["organization_name"] == "Approved Corp" for i in pending_items)

    item = next(i for i in pending_items if i["organization_name"] == "Pending Inc")
    assert item["email"] == "pending_org@test.com"
    assert item["approval_status"] == "pending"


def test_admin_update_organization_approval_workflow(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Admin can approve and reject organizations, with session reviewer stamped."""
    admin = create_test_user(real_db_session, email="admin_reviewer@test.com", role=UserRole.ADMIN)
    org_user, _ = create_test_organization(
        real_db_session,
        email="corp_rev@test.com",
        organization_name="Review Corp",
        approval_status=ApprovalStatus.PENDING,
    )

    login_test_user(real_db_client, admin.email)

    # Approve with note
    approve_resp = real_db_client.put(
        f"/api/admin/organizations/{org_user.id}/approval",
        json={"approval_status": "approved", "approval_note": "Legitimate enterprise."},
    )
    assert approve_resp.status_code == 200
    app_data = approve_resp.json()
    assert app_data["approval_status"] == "approved"
    assert app_data["approval_note"] == "Legitimate enterprise."
    assert app_data["reviewed_by"] == admin.id
    assert app_data["reviewed_at"] is not None

    # Check that client cannot forge reviewer
    resp_forge = real_db_client.put(
        f"/api/admin/organizations/{org_user.id}/approval",
        json={"approval_status": "approved", "reviewed_by": 999},
    )
    assert resp_forge.status_code == 422

    # Reject with note
    reject_resp = real_db_client.put(
        f"/api/admin/organizations/{org_user.id}/approval",
        json={"approval_status": "rejected", "approval_note": "Missing corporate registration."},
    )
    assert reject_resp.status_code == 200
    assert reject_resp.json()["approval_status"] == "rejected"
    assert reject_resp.json()["approval_note"] == "Missing corporate registration."


def test_get_organization_me_includes_approval_status(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """GET /api/organizations/me includes approval_status and approval_note."""
    org_user, profile = create_test_organization(
        real_db_session,
        email="my_org_status@test.com",
        organization_name="My Org Ltd",
        approval_status=ApprovalStatus.PENDING,
    )
    profile.approval_note = "Awaiting verification"
    real_db_session.commit()

    login_test_user(real_db_client, org_user.email)
    resp = real_db_client.get("/api/organizations/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["approval_status"] == "pending"
    assert data["approval_note"] == "Awaiting verification"
