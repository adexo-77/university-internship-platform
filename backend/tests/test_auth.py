"""Integration tests for authentication, sessions, security, and role checks."""

import hashlib
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import require_roles
from app.core.security import SESSION_COOKIE_NAME, hash_password
from app.main import app
from app.models.session import Session as SessionModel
from app.models.user import User, UserRole

# Attach a test-only route to verify role enforcement dependencies
role_test_router = APIRouter(prefix="/api/test-roles", tags=["test"])
require_admin_role = require_roles(UserRole.ADMIN)


@role_test_router.get("/admin-only")
def admin_only_endpoint(
    current_user: User = Depends(require_admin_role),
) -> dict[str, str]:
    return {"message": f"Welcome admin {current_user.full_name}"}


app.include_router(role_test_router)


def test_register_student_and_organization(real_db_client: TestClient) -> None:
    # 1. Register student
    resp_student = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "student1@example.com",
            "password": "Password123!",
            "full_name": "Test Student",
            "role": "student",
        },
    )
    assert resp_student.status_code == 201
    data_student = resp_student.json()
    assert data_student["email"] == "student1@example.com"
    assert data_student["role"] == "student"
    assert "password_hash" not in data_student
    assert SESSION_COOKIE_NAME in resp_student.cookies

    # 2. Register organization
    resp_org = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "org1@example.com",
            "password": "Password123!",
            "full_name": "Acme Corp",
            "role": "organization",
        },
    )
    assert resp_org.status_code == 201
    data_org = resp_org.json()
    assert data_org["email"] == "org1@example.com"
    assert data_org["role"] == "organization"


def test_register_rejects_instructor_and_admin(real_db_client: TestClient) -> None:
    resp_instructor = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "instructor@example.com",
            "password": "Password123!",
            "full_name": "Instructor Name",
            "role": "instructor",
        },
    )
    assert resp_instructor.status_code == 422

    resp_admin = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "admin@example.com",
            "password": "Password123!",
            "full_name": "Admin Name",
            "role": "admin",
        },
    )
    assert resp_admin.status_code == 422


def test_register_duplicate_email(real_db_client: TestClient) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "full_name": "First User",
        "role": "student",
    }
    resp1 = real_db_client.post("/api/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = real_db_client.post(
        "/api/auth/register",
        json={**payload, "full_name": "Second User"},
    )
    assert resp2.status_code == 409
    body = resp2.json()
    assert body["code"] == "EMAIL_ALREADY_REGISTERED"


def test_register_password_length_validation(real_db_client: TestClient) -> None:
    # Short password (< 8 chars)
    resp_short = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "short@example.com",
            "password": "short",
            "full_name": "Short Password",
            "role": "student",
        },
    )
    assert resp_short.status_code == 422

    # Long password (> 128 chars)
    resp_long = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "long@example.com",
            "password": "a" * 129,
            "full_name": "Long Password",
            "role": "student",
        },
    )
    assert resp_long.status_code == 422


def test_email_normalization(real_db_client: TestClient, real_db_session: Session) -> None:
    resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "  MixedCase.Student@Example.COM  ",
            "password": "Password123!",
            "full_name": "Normalized Student",
            "role": "student",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "mixedcase.student@example.com"

    # Verify directly in database
    user = real_db_session.scalar(select(User).where(User.email == "mixedcase.student@example.com"))
    assert user is not None
    assert user.email == "mixedcase.student@example.com"


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
