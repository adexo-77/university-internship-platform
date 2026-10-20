"""Integration tests for user activation lifecycle and admin password reset."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_admin_self_deactivation_and_last_admin_protection(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """An admin cannot deactivate themselves and the last active admin cannot be deactivated."""
    admin1 = create_test_user(real_db_session, email="only_admin@example.com", role=UserRole.ADMIN)
    login_test_user(real_db_client, admin1.email)

    # Self-deactivation guard
    resp_self = real_db_client.patch(f"/api/admin/users/{admin1.id}", json={"is_active": False})
    assert resp_self.status_code == 409
    assert resp_self.json()["code"] == "SELF_DEACTIVATION_FORBIDDEN"

    # Last active admin guard (another admin tries to deactivate the last admin)
    admin2 = create_test_user(real_db_session, email="admin2@example.com", role=UserRole.ADMIN)
    login_test_user(real_db_client, admin2.email)

    # Deactivate admin1
    resp_deact1 = real_db_client.patch(f"/api/admin/users/{admin1.id}", json={"is_active": False})
    assert resp_deact1.status_code == 200

    admin1.is_active = False
    real_db_session.commit()

    resp_deact2 = real_db_client.patch(f"/api/admin/users/{admin2.id}", json={"is_active": False})
    assert resp_deact2.status_code == 409


def test_deactivation_kills_sessions_and_blocks_login(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Deactivating a user immediately revokes all sessions and blocks login until reactivated."""
    admin = create_test_user(real_db_session, email="admin_ops@example.com", role=UserRole.ADMIN)
    inst = create_test_user(
        real_db_session,
        email="target_inst@example.com",
        role=UserRole.INSTRUCTOR,
        password="OldPassword123!",
    )

    # Target instructor logs in and acquires session cookie
    with TestClient(app) as inst_client:
        login_test_user(inst_client, inst.email, "OldPassword123!")
        me_resp = inst_client.get("/api/auth/me")
        assert me_resp.status_code == 200

        # Admin deactivates target instructor
        login_test_user(real_db_client, admin.email)
        deact_resp = real_db_client.patch(f"/api/admin/users/{inst.id}", json={"is_active": False})
        assert deact_resp.status_code == 200
        assert deact_resp.json()["is_active"] is False

        # Target instructor's previous session is immediately dead
        dead_resp = inst_client.get("/api/auth/me")
        assert dead_resp.status_code == 401

        # Inactive instructor cannot log in
        login_attempt = inst_client.post(
            "/api/auth/login", json={"email": inst.email, "password": "OldPassword123!"}
        )
        assert login_attempt.status_code == 401

        # Reactivating allows login again
        react_resp = real_db_client.patch(f"/api/admin/users/{inst.id}", json={"is_active": True})
        assert react_resp.status_code == 200
        assert react_resp.json()["is_active"] is True

        login_success = inst_client.post(
            "/api/auth/login", json={"email": inst.email, "password": "OldPassword123!"}
        )
        assert login_success.status_code == 200


def test_admin_password_reset_kills_sessions_and_allows_login(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Admin password reset sets a new password, deletes active sessions, and works for login."""
    admin = create_test_user(real_db_session, email="admin_pwd@example.com", role=UserRole.ADMIN)
    student = create_test_user(
        real_db_session,
        email="target_student@example.com",
        role=UserRole.STUDENT,
        password="OldPassword123!",
    )

    with TestClient(app) as student_client:
        login_test_user(student_client, student.email, "OldPassword123!")
        assert student_client.get("/api/auth/me").status_code == 200

        # Admin resets student password
        login_test_user(real_db_client, admin.email)
        reset_resp = real_db_client.put(
            f"/api/admin/users/{student.id}/password", json={"password": "NewSecretPassword123!"}
        )
        assert reset_resp.status_code == 200
        assert "password_hash" not in reset_resp.json()

        # Previous session is invalidated
        assert student_client.get("/api/auth/me").status_code == 401

        # Old password no longer works
        assert (
            student_client.post(
                "/api/auth/login", json={"email": student.email, "password": "OldPassword123!"}
            ).status_code
            == 401
        )

        # New password works
        new_login = student_client.post(
            "/api/auth/login", json={"email": student.email, "password": "NewSecretPassword123!"}
        )
        assert new_login.status_code == 200
        assert new_login.json()["email"] == student.email
