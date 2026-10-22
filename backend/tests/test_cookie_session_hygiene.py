"""Tests for cookie security, production configuration guards, and session purging."""

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings, validate_production_configuration
from app.core.security import hash_session_token
from app.models.session import Session as SessionModel
from app.models.user import UserRole
from app.services.auth import AuthService
from tests.factories import create_test_user


def test_production_session_cookie_flags(real_db_client: TestClient) -> None:
    """Session cookies include Secure (in prod), HttpOnly, and SameSite=lax."""
    # Register a user to trigger cookie generation
    resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "cookie.hygiene@example.com",
            "password": "Password123!",
            "full_name": "Cookie User",
            "role": "student",
        },
    )
    assert resp.status_code == 201
    set_cookie_header = resp.headers.get("set-cookie", "")
    assert "HttpOnly" in set_cookie_header
    assert "SameSite=lax" in set_cookie_header or "samesite=lax" in set_cookie_header


def test_production_startup_fails_if_cookie_secure_is_false() -> None:
    """Production startup must fail with a clear message if COOKIE_SECURE is False."""
    cfg = Settings(
        DATABASE_URL="postgresql+psycopg://user:pass@localhost/db",
        TEST_DATABASE_URL="postgresql+psycopg://user:pass@localhost/test_db",
        ENVIRONMENT="development",
    )
    # Simulate production mode with insecure cookie setting
    cfg.ENVIRONMENT = "production"
    cfg.COOKIE_SECURE = False

    with pytest.raises(RuntimeError, match="COOKIE_SECURE must be True"):
        validate_production_configuration(cfg)


def test_production_startup_fails_if_cors_origins_contains_localhost() -> None:
    """Production startup must fail with a clear message if CORS_ORIGINS contains localhost."""
    cfg = Settings(
        DATABASE_URL="postgresql+psycopg://user:pass@localhost/db",
        TEST_DATABASE_URL="postgresql+psycopg://user:pass@localhost/test_db",
        ENVIRONMENT="development",
    )
    cfg.ENVIRONMENT = "production"
    cfg.COOKIE_SECURE = True
    cfg.CORS_ORIGINS = ["https://app.university.edu", "http://localhost:5173"]

    with pytest.raises(RuntimeError, match="CORS_ORIGINS cannot contain localhost"):
        validate_production_configuration(cfg)


def test_expired_sessions_purged_on_login(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Expired sessions are deleted from database upon successful user authentication."""
    email = "purge.test@example.com"
    pwd = "Password123!"
    user = create_test_user(db=real_db_session, email=email, role=UserRole.STUDENT, password=pwd)

    # Seed an expired session for this user
    past_time = datetime.now(UTC) - timedelta(hours=2)
    expired_session = SessionModel(
        user_id=user.id,
        token_hash=hash_session_token("expired_dummy_token_12345"),
        expires_at=past_time,
    )
    real_db_session.add(expired_session)
    real_db_session.commit()

    # Verify session exists in DB before login
    found_before = real_db_session.scalar(
        select(SessionModel).where(SessionModel.user_id == user.id)
    )
    assert found_before is not None

    # Perform login
    resp = real_db_client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert resp.status_code == 200

    # Expired session must be purged; only the new active session should exist
    sessions = real_db_session.scalars(
        select(SessionModel).where(SessionModel.user_id == user.id)
    ).all()
    assert len(sessions) == 1
    assert sessions[0].expires_at > datetime.now(UTC)


def test_purge_expired_sessions_service_method(real_db_session: Session) -> None:
    """Direct invocation of AuthService.purge_expired_sessions cleans expired rows."""
    user = create_test_user(
        db=real_db_session,
        email="direct.purge@example.com",
        role=UserRole.STUDENT,
        password="Password123!",
    )
    past_time = datetime.now(UTC) - timedelta(days=1)
    expired = SessionModel(
        user_id=user.id,
        token_hash=hash_session_token("stale_token_abc"),
        expires_at=past_time,
    )
    real_db_session.add(expired)
    real_db_session.commit()

    count = AuthService.purge_expired_sessions(real_db_session)
    assert count >= 1

    remaining = real_db_session.scalar(
        select(SessionModel).where(SessionModel.token_hash == hash_session_token("stale_token_abc"))
    )
    assert remaining is None
