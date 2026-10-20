"""Integration tests for user self password change endpoint."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_change_password_requires_authentication(real_db_client: TestClient) -> None:
    """Unauthenticated call to /api/auth/change-password returns 401."""
    real_db_client.cookies.clear()
    resp = real_db_client.post(
        "/api/auth/change-password",
        json={"current_password": "OldPassword123!", "new_password": "NewPassword123!"},
    )
    assert resp.status_code == 401


def test_change_password_validation_rules(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Password change validates length, same password, and wrong current password."""
    user = create_test_user(
        real_db_session,
        email="pwd_rules@test.com",
        role=UserRole.STUDENT,
        password="OriginalPassword123!",
    )
    login_test_user(real_db_client, user.email, "OriginalPassword123!")

    # Same password rejected with 422
    resp_same = real_db_client.post(
        "/api/auth/change-password",
        json={"current_password": "OriginalPassword123!", "new_password": "OriginalPassword123!"},
    )
    assert resp_same.status_code == 422

    # Short password rejected
    resp_short = real_db_client.post(
        "/api/auth/change-password",
        json={"current_password": "OriginalPassword123!", "new_password": "short"},
    )
    assert resp_short.status_code == 422

    # Extra fields rejected
    resp_extra = real_db_client.post(
        "/api/auth/change-password",
        json={
            "current_password": "OriginalPassword123!",
            "new_password": "NewSecretPassword123!",
            "is_admin": True,
        },
    )
    assert resp_extra.status_code == 422

    # Wrong current password gives 401 with identical message to login (no hint)
    resp_wrong = real_db_client.post(
        "/api/auth/change-password",
        json={"current_password": "WrongPassword999!", "new_password": "NewSecretPassword123!"},
    )
    assert resp_wrong.status_code == 401
    assert resp_wrong.json()["detail"] == "Invalid email or password"
    assert resp_wrong.json()["code"] == "INVALID_CREDENTIALS"


def test_change_password_session_handling_and_login(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Password change succeeds, keeps current session alive, kills other sessions,
    and updates login credentials.
    """
    user = create_test_user(
        real_db_session,
        email="pwd_sess@test.com",
        role=UserRole.INSTRUCTOR,
        password="InitPassword123!",
    )

    # Session 1 (will perform password change)
    client1 = real_db_client
    login_test_user(client1, user.email, "InitPassword123!")

    # Session 2 (should be invalidated)
    with TestClient(app) as client2:
        login_test_user(client2, user.email, "InitPassword123!")

        assert client1.get("/api/auth/me").status_code == 200
        assert client2.get("/api/auth/me").status_code == 200

        # Perform password change on client1
        resp_change = client1.post(
            "/api/auth/change-password",
            json={"current_password": "InitPassword123!", "new_password": "UpdatedPassword123!"},
        )
        assert resp_change.status_code == 200

        # Client1 session remains valid and active
        me_resp = client1.get("/api/auth/me")
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == user.email

        # Client2 other session has been terminated
        assert client2.get("/api/auth/me").status_code == 401

        # Login with old password fails
        assert (
            client1.post(
                "/api/auth/login", json={"email": user.email, "password": "InitPassword123!"}
            ).status_code
            == 401
        )

        # Login with new password succeeds
        login_new = client1.post(
            "/api/auth/login", json={"email": user.email, "password": "UpdatedPassword123!"}
        )
        assert login_new.status_code == 200
