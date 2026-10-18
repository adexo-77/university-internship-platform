"""Integration tests for user login, credentials verification, and security sanitization."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import SESSION_COOKIE_NAME, hash_password
from app.models.user import User, UserRole


def test_login_success_sets_cookie(real_db_client: TestClient) -> None:
    real_db_client.post(
        "/api/auth/register",
        json={
            "email": "login_test@example.com",
            "password": "Password123!",
            "full_name": "Login Test",
            "role": "student",
        },
    )

    # Login
    login_resp = real_db_client.post(
        "/api/auth/login",
        json={"email": "login_test@example.com", "password": "Password123!"},
    )
    assert login_resp.status_code == 200
    assert "password_hash" not in login_resp.json()
    assert SESSION_COOKIE_NAME in login_resp.cookies


def test_wrong_password_and_unknown_email_give_identical_response(
    real_db_client: TestClient,
) -> None:
    real_db_client.post(
        "/api/auth/register",
        json={
            "email": "exists@example.com",
            "password": "CorrectPassword123!",
            "full_name": "Exists User",
            "role": "student",
        },
    )

    # Wrong password for existing user
    resp_wrong = real_db_client.post(
        "/api/auth/login",
        json={"email": "exists@example.com", "password": "WrongPassword!"},
    )

    # Unknown email
    resp_unknown = real_db_client.post(
        "/api/auth/login",
        json={"email": "nonexistent@example.com", "password": "AnyPassword123!"},
    )

    assert resp_wrong.status_code == 401
    assert resp_unknown.status_code == 401
    assert resp_wrong.json() == resp_unknown.json()
    assert resp_wrong.json() == {
        "detail": "Invalid email or password",
        "code": "INVALID_CREDENTIALS",
    }


def test_inactive_user_cannot_login(real_db_client: TestClient, real_db_session: Session) -> None:
    # Seed inactive user
    user = User(
        email="inactive@example.com",
        password_hash=hash_password("Password123!"),
        full_name="Inactive User",
        role=UserRole.STUDENT,
        is_active=False,
    )
    real_db_session.add(user)
    real_db_session.commit()

    resp = real_db_client.post(
        "/api/auth/login",
        json={"email": "inactive@example.com", "password": "Password123!"},
    )
    assert resp.status_code == 401
    assert resp.json() == {
        "detail": "Invalid email or password",
        "code": "INVALID_CREDENTIALS",
    }


def test_password_hash_never_in_responses(real_db_client: TestClient) -> None:
    reg_resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "leak_test@example.com",
            "password": "Password123!",
            "full_name": "Leak Check",
            "role": "student",
        },
    )
    assert "password" not in reg_resp.json()
    assert "password_hash" not in reg_resp.json()

    login_resp = real_db_client.post(
        "/api/auth/login",
        json={"email": "leak_test@example.com", "password": "Password123!"},
    )
    assert "password" not in login_resp.json()
    assert "password_hash" not in login_resp.json()

    me_resp = real_db_client.get("/api/auth/me")
    assert "password" not in me_resp.json()
    assert "password_hash" not in me_resp.json()
