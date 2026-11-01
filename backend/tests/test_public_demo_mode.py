"""Integration tests verifying public demo mode restrictions and guarantees."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user

DEMO_STUDENT = "abel.tesfaye@example.com"
DEMO_INSTRUCTOR = "tadesse.bekele@example.com"


def test_public_demo_health_flag(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    """GET /api/health must accurately reflect the DEMO_PUBLIC_MODE setting."""
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", False)
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["public_demo"] is False

    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", True)
    resp_demo = client.get("/api/health")
    assert resp_demo.status_code == 200
    assert resp_demo.json()["public_demo"] is True


def test_demo_account_cannot_change_password_in_public_mode(
    real_db_client: TestClient, real_db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Seeded demo accounts cannot change password when DEMO_PUBLIC_MODE=True."""
    user = create_test_user(
        real_db_session, email=DEMO_STUDENT, role=UserRole.STUDENT, password="OldPassword123!"
    )
    login_test_user(real_db_client, user.email, "OldPassword123!")

    # When public demo is enabled -> 403 Disabled in the public demo
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", True)
    resp_blocked = real_db_client.post(
        "/api/auth/change-password",
        json={"current_password": "OldPassword123!", "new_password": "NewSecretPassword1!"},
    )
    assert resp_blocked.status_code == 403
    assert resp_blocked.json()["detail"] == "Disabled in the public demo"

    # When public demo is disabled -> 200 OK
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", False)
    resp_ok = real_db_client.post(
        "/api/auth/change-password",
        json={"current_password": "OldPassword123!", "new_password": "NewSecretPassword1!"},
    )
    assert resp_ok.status_code == 200


def test_admin_cannot_reset_demo_account_password_in_public_mode(
    real_db_client: TestClient, real_db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Admins cannot reset passwords for seeded demo accounts in public demo mode."""
    admin = create_test_user(real_db_session, email="custom_admin@example.com", role=UserRole.ADMIN)
    target = create_test_user(real_db_session, email=DEMO_STUDENT, role=UserRole.STUDENT)
    login_test_user(real_db_client, admin.email)

    # When public demo is enabled -> 403 Forbidden
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", True)
    resp_blocked = real_db_client.put(
        f"/api/admin/users/{target.id}/password",
        json={"password": "ResetPassword123!"},
    )
    assert resp_blocked.status_code == 403
    assert resp_blocked.json()["detail"] == "Disabled in the public demo"

    # When public demo is disabled -> 200 OK
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", False)
    resp_ok = real_db_client.put(
        f"/api/admin/users/{target.id}/password",
        json={"password": "ResetPassword123!"},
    )
    assert resp_ok.status_code == 200


def test_demo_account_cannot_be_deactivated_in_public_mode(
    real_db_client: TestClient, real_db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Seeded demo accounts cannot be deactivated when DEMO_PUBLIC_MODE=True."""
    admin = create_test_user(
        real_db_session, email="custom_admin2@example.com", role=UserRole.ADMIN
    )
    demo_inst = create_test_user(real_db_session, email=DEMO_INSTRUCTOR, role=UserRole.INSTRUCTOR)
    login_test_user(real_db_client, admin.email)

    # When public demo is enabled -> 403 Forbidden
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", True)
    resp_blocked = real_db_client.patch(
        f"/api/admin/users/{demo_inst.id}",
        json={"is_active": False},
    )
    assert resp_blocked.status_code == 403
    assert resp_blocked.json()["detail"] == "Disabled in the public demo"

    # When public demo is disabled -> 200 OK
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", False)
    resp_ok = real_db_client.patch(
        f"/api/admin/users/{demo_inst.id}",
        json={"is_active": False},
    )
    assert resp_ok.status_code == 200


def test_demo_account_role_cannot_be_changed_in_public_mode(
    real_db_client: TestClient, real_db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Seeded demo account roles cannot be changed when DEMO_PUBLIC_MODE=True."""
    admin = create_test_user(
        real_db_session, email="custom_admin3@example.com", role=UserRole.ADMIN
    )
    demo_student = create_test_user(real_db_session, email=DEMO_STUDENT, role=UserRole.STUDENT)
    login_test_user(real_db_client, admin.email)

    # When public demo is enabled -> 403 Forbidden
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", True)
    resp_blocked = real_db_client.patch(
        f"/api/admin/users/{demo_student.id}",
        json={"role": "instructor"},
    )
    assert resp_blocked.status_code == 403
    assert resp_blocked.json()["detail"] == "Disabled in the public demo"

    # When public demo is disabled -> 200 OK
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", False)
    resp_ok = real_db_client.patch(
        f"/api/admin/users/{demo_student.id}",
        json={"role": "instructor"},
    )
    assert resp_ok.status_code == 200


def test_admin_cannot_create_privileged_roles_in_public_mode(
    real_db_client: TestClient, real_db_session: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Admins cannot provision admin or coordinator roles when DEMO_PUBLIC_MODE=True."""
    admin = create_test_user(
        real_db_session, email="custom_admin4@example.com", role=UserRole.ADMIN
    )
    login_test_user(real_db_client, admin.email)

    # In public demo mode: admin creation blocked
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", True)
    resp_admin = real_db_client.post(
        "/api/admin/users",
        json={
            "full_name": "New Admin",
            "email": "new.admin@example.org",
            "password": "Password123!",
            "role": "admin",
        },
    )
    assert resp_admin.status_code == 403
    assert resp_admin.json()["detail"] == "Disabled in the public demo"

    # In public demo mode: coordinator creation blocked
    resp_coord = real_db_client.post(
        "/api/admin/users",
        json={
            "full_name": "New Coord",
            "email": "new.coord@example.org",
            "password": "Password123!",
            "role": "coordinator",
        },
    )
    assert resp_coord.status_code == 403
    assert resp_coord.json()["detail"] == "Disabled in the public demo"

    # In public demo mode: instructor creation allowed
    resp_inst = real_db_client.post(
        "/api/admin/users",
        json={
            "full_name": "New Instructor",
            "email": "new.instructor@example.org",
            "password": "Password123!",
            "role": "instructor",
        },
    )
    assert resp_inst.status_code == 201

    # When public demo is disabled: admin and coordinator creation allowed
    monkeypatch.setattr(settings, "DEMO_PUBLIC_MODE", False)
    resp_admin_allowed = real_db_client.post(
        "/api/admin/users",
        json={
            "full_name": "Allowed Admin",
            "email": "allowed.admin@example.org",
            "password": "Password123!",
            "role": "admin",
        },
    )
    assert resp_admin_allowed.status_code == 201
