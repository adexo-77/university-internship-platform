"""Integration tests for user session lifecycle, cookies, expiration, and role guards."""

import hashlib
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import SESSION_COOKIE_NAME, hash_password
from app.models.session import Session as SessionModel
from app.models.user import User, UserRole


def test_me_without_cookie_gives_401(real_db_client: TestClient) -> None:
    resp = real_db_client.get("/api/auth/me")
    assert resp.status_code == 401
    assert resp.json()["code"] == "UNAUTHORIZED"


def test_logout_invalidates_session(real_db_client: TestClient) -> None:
    real_db_client.post(
        "/api/auth/register",
        json={
            "email": "logout@example.com",
            "password": "Password123!",
            "full_name": "Logout User",
            "role": "student",
        },
    )

    # Verify authenticated
    me_resp = real_db_client.get("/api/auth/me")
    assert me_resp.status_code == 200

    # Logout
    logout_resp = real_db_client.post("/api/auth/logout")
    assert logout_resp.status_code == 200

    # Next call without cookie fails
    after_resp = real_db_client.get("/api/auth/me")
    assert after_resp.status_code == 401


def test_expired_session_gives_401(real_db_client: TestClient, real_db_session: Session) -> None:
    real_db_client.post(
        "/api/auth/register",
        json={
            "email": "expired@example.com",
            "password": "Password123!",
            "full_name": "Expired User",
            "role": "student",
        },
    )

    # Manually expire all sessions for this user in DB
    user = real_db_session.scalar(select(User).where(User.email == "expired@example.com"))
    assert user is not None
    sessions = real_db_session.scalars(
        select(SessionModel).where(SessionModel.user_id == user.id)
    ).all()
    for s in sessions:
        s.expires_at = datetime.now(UTC) - timedelta(hours=1)
    real_db_session.commit()

    # Now calling /me with the cookie fails
    resp = real_db_client.get("/api/auth/me")
    assert resp.status_code == 401


def test_require_roles_permissions(real_db_client: TestClient, real_db_session: Session) -> None:
    # 1. Unauthenticated -> 401
    resp_unauth = real_db_client.get("/api/test-roles/admin-only")
    assert resp_unauth.status_code == 401

    # 2. Student logged in -> 403
    real_db_client.post(
        "/api/auth/register",
        json={
            "email": "student_role@example.com",
            "password": "Password123!",
            "full_name": "Student Role",
            "role": "student",
        },
    )
    resp_forbidden = real_db_client.get("/api/test-roles/admin-only")
    assert resp_forbidden.status_code == 403
    assert resp_forbidden.json()["code"] == "FORBIDDEN"

    # 3. Seed admin user in DB and login
    admin_user = User(
        email="admin_role@example.com",
        password_hash=hash_password("AdminPassword123!"),
        full_name="Admin Boss",
        role=UserRole.ADMIN,
        is_active=True,
    )
    real_db_session.add(admin_user)
    real_db_session.commit()

    # Login as admin
    real_db_client.post(
        "/api/auth/login",
        json={"email": "admin_role@example.com", "password": "AdminPassword123!"},
    )
    resp_allowed = real_db_client.get("/api/test-roles/admin-only")
    assert resp_allowed.status_code == 200
    assert "Welcome admin Admin Boss" in resp_allowed.json()["message"]


def test_database_stores_token_hash_not_raw_token(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "token_check@example.com",
            "password": "Password123!",
            "full_name": "Token Check",
            "role": "student",
        },
    )
    raw_token = resp.cookies.get(SESSION_COOKIE_NAME)
    assert raw_token is not None

    user = real_db_session.scalar(select(User).where(User.email == "token_check@example.com"))
    assert user is not None
    db_session = real_db_session.scalar(select(SessionModel).where(SessionModel.user_id == user.id))
    assert db_session is not None
    # Token hash in DB must NOT equal raw token
    assert db_session.token_hash != raw_token
    # Token hash in DB must equal SHA-256 of raw token
    expected_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    assert db_session.token_hash == expected_hash
