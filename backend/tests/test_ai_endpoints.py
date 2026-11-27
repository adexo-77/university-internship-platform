"""Integration tests for GET /api/ai/status and PUT /api/ai/consent endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import UserRole
from tests.factories import create_test_user


def test_ai_status_returns_disabled_by_default(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """AI is OFF by default; no consent; quota values are numeric."""
    email, pwd = "ai_ep_status@example.com", "ValidPassword123!"
    create_test_user(db=real_db_session, email=email, role=UserRole.STUDENT, password=pwd)
    real_db_client.post("/api/auth/login", json={"email": email, "password": pwd})

    resp = real_db_client.get("/api/ai/status")
    assert resp.status_code == 200
    body = resp.json()
    assert body["enabled"] is False
    assert body["consented"] is False
    assert isinstance(body["remaining_quota"], int)
    assert isinstance(body["daily_limit"], int)


def test_ai_consent_set_true_then_clear(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """PUT consent=true then false toggles the consented field correctly."""
    email, pwd = "ai_ep_consent@example.com", "ValidPassword123!"
    create_test_user(db=real_db_session, email=email, role=UserRole.STUDENT, password=pwd)
    real_db_client.post("/api/auth/login", json={"email": email, "password": pwd})

    resp = real_db_client.put("/api/ai/consent", json={"consented": True})
    assert resp.status_code == 200
    assert resp.json()["consented"] is True

    resp2 = real_db_client.put("/api/ai/consent", json={"consented": False})
    assert resp2.status_code == 200
    assert resp2.json()["consented"] is False


def test_ai_status_persisted_after_consent(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """After opting in, GET /api/ai/status shows consented=true."""
    email, pwd = "ai_ep_persist@example.com", "ValidPassword123!"
    create_test_user(db=real_db_session, email=email, role=UserRole.STUDENT, password=pwd)
    real_db_client.post("/api/auth/login", json={"email": email, "password": pwd})
    real_db_client.put("/api/ai/consent", json={"consented": True})

    status_resp = real_db_client.get("/api/ai/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["consented"] is True


def test_ai_consent_rejects_extra_fields(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Extra JSON fields are rejected (strict schema with extra='forbid')."""
    email, pwd = "ai_ep_extra@example.com", "ValidPassword123!"
    create_test_user(db=real_db_session, email=email, role=UserRole.STUDENT, password=pwd)
    real_db_client.post("/api/auth/login", json={"email": email, "password": pwd})

    resp = real_db_client.put(
        "/api/ai/consent", json={"consented": True, "unexpected_field": "bad"}
    )
    assert resp.status_code == 422


def test_ai_status_requires_auth(real_db_client: TestClient) -> None:
    """Unauthenticated GET /api/ai/status returns 401."""
    real_db_client.cookies.clear()
    resp = real_db_client.get("/api/ai/status")
    assert resp.status_code == 401


def test_ai_consent_requires_auth(real_db_client: TestClient) -> None:
    """Unauthenticated PUT /api/ai/consent returns 401."""
    real_db_client.cookies.clear()
    resp = real_db_client.put("/api/ai/consent", json={"consented": True})
    assert resp.status_code == 401


@pytest.mark.parametrize("role", ["instructor", "organization", "coordinator", "admin"])
def test_ai_status_accessible_by_all_roles(
    real_db_client: TestClient, real_db_session: Session, role: str
) -> None:
    """Every authenticated role can read their own AI status."""
    from app.models.user import UserRole as UR

    role_map = {
        "instructor": UR.INSTRUCTOR,
        "organization": UR.ORGANIZATION,
        "coordinator": UR.COORDINATOR,
        "admin": UR.ADMIN,
    }
    email = f"ai_ep_role_{role}@example.com"
    pwd = "ValidPassword123!"
    create_test_user(db=real_db_session, email=email, role=role_map[role], password=pwd)
    real_db_client.post("/api/auth/login", json={"email": email, "password": pwd})

    resp = real_db_client.get("/api/ai/status")
    assert resp.status_code == 200
    assert "enabled" in resp.json()
