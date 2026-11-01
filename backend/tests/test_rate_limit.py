"""Tests for sliding-window rate limiter with controllable clock."""

from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import RateLimitExceededException
from app.core.rate_limit import get_client_ip, rate_limiter
from app.models.user import UserRole
from tests.factories import create_test_user


class ControllableClock:
    """Mock clock that can be manually advanced for testing sliding windows."""

    def __init__(self, start_time: float = 1_000_000.0) -> None:
        self.current_time = start_time

    def __call__(self) -> float:
        return self.current_time

    def advance(self, seconds: float) -> None:
        self.current_time += seconds


@pytest.fixture
def mock_clock() -> Generator[ControllableClock, None, None]:
    clock = ControllableClock()
    rate_limiter.enabled = True
    rate_limiter.set_clock(clock)
    yield clock
    rate_limiter.enabled = False


def test_login_failed_attempts_rate_limit_per_email_and_ip(
    real_db_client: TestClient, mock_clock: ControllableClock
) -> None:
    """5 failed attempts per (IP + email) trigger 429; advancing clock resets window."""
    bad_payload = {"email": "victim@example.com", "password": "wrongpassword123"}
    for _ in range(5):
        resp = real_db_client.post("/api/auth/login", json=bad_payload)
        assert resp.status_code == 401

    resp_blocked = real_db_client.post("/api/auth/login", json=bad_payload)
    assert resp_blocked.status_code == 429
    assert resp_blocked.headers.get("Retry-After") is not None
    assert resp_blocked.json()["code"] == "RATE_LIMIT_EXCEEDED"

    # Advance clock past the 15-minute window (900 seconds)
    mock_clock.advance(901)
    resp_after = real_db_client.post("/api/auth/login", json=bad_payload)
    assert resp_after.status_code == 401


@pytest.mark.usefixtures("mock_clock")
def test_successful_login_resets_email_counter(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """A successful login resets the failure counter for (client IP + email)."""
    email = "user.reset@example.com"
    pwd = "ValidPassword123!"
    create_test_user(db=real_db_session, email=email, role=UserRole.STUDENT, password=pwd)

    # 4 failed attempts
    for _ in range(4):
        resp = real_db_client.post("/api/auth/login", json={"email": email, "password": "wrong"})
        assert resp.status_code == 401

    # 1 successful login
    resp_success = real_db_client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert resp_success.status_code == 200

    # Counter is reset, so 4 more failures are allowed before 429
    for _ in range(4):
        resp = real_db_client.post("/api/auth/login", json={"email": email, "password": "wrong"})
        assert resp.status_code == 401


@pytest.mark.usefixtures("mock_clock")
def test_login_ip_limit_triggers_429(real_db_client: TestClient) -> None:
    """20 login attempts from the same IP trigger 429."""
    for i in range(20):
        resp = real_db_client.post(
            "/api/auth/login",
            json={"email": f"attacker_{i}@example.com", "password": "bad"},
        )
        assert resp.status_code in (401, 429)

    resp_blocked = real_db_client.post(
        "/api/auth/login", json={"email": "attacker_21@example.com", "password": "bad"}
    )
    assert resp_blocked.status_code == 429
    assert int(resp_blocked.headers.get("Retry-After", 0)) > 0


@pytest.mark.usefixtures("mock_clock")
def test_register_rate_limit_per_ip(real_db_client: TestClient) -> None:
    """10 registrations per hour per IP; 11th triggers 429."""
    for i in range(10):
        resp = real_db_client.post(
            "/api/auth/register",
            json={
                "email": f"newstudent_{i}@example.com",
                "password": "Password123!",
                "full_name": f"Student {i}",
                "role": "student",
            },
        )
        assert resp.status_code == 201

    resp_blocked = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "newstudent_11@example.com",
            "password": "Password123!",
            "full_name": "Student 11",
            "role": "student",
        },
    )
    assert resp_blocked.status_code == 429


@pytest.mark.usefixtures("mock_clock")
def test_change_password_rate_limit_per_user(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """5 change-password requests per 15 minutes per user; 6th triggers 429."""
    email = "changepwd@example.com"
    pwd = "OriginalPassword123!"
    create_test_user(db=real_db_session, email=email, role=UserRole.STUDENT, password=pwd)

    # Login to acquire session cookie
    login_resp = real_db_client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert login_resp.status_code == 200

    for i in range(5):
        resp = real_db_client.post(
            "/api/auth/change-password",
            json={
                "current_password": "wrongpassword!",
                "new_password": f"NewValidPass{i}!",
            },
        )
        assert resp.status_code == 401

    resp_blocked = real_db_client.post(
        "/api/auth/change-password",
        json={
            "current_password": "wrongpassword!",
            "new_password": "NewValidPass99!",
        },
    )
    assert resp_blocked.status_code == 429


def test_client_ip_resolution_respects_trusted_proxy() -> None:
    """Test get_client_ip respects TRUSTED_PROXY configuration and uses proxy-set IP."""
    req = MagicMock(spec=Request)
    req.headers = {"x-forwarded-for": "198.51.100.1, 203.0.113.195"}
    req.client = MagicMock(host="10.0.0.1")

    # TRUSTED_PROXY off (default)
    settings.TRUSTED_PROXY = False
    assert get_client_ip(req) == "10.0.0.1"

    # TRUSTED_PROXY on: extracts the trusted proxy set/appended address (last entry)
    settings.TRUSTED_PROXY = True
    assert get_client_ip(req) == "203.0.113.195"
    settings.TRUSTED_PROXY = False


def test_client_ip_spoofing_attempt_rejected() -> None:
    """A client supplying spoofed X-Forwarded-For prefixes cannot forge their IP."""
    req = MagicMock(spec=Request)
    # Malicious client sends spoofed 1.2.3.4, trusted nginx appends real visitor 198.51.100.42
    req.headers = {"x-forwarded-for": "1.2.3.4, 5.6.7.8, 198.51.100.42"}
    req.client = MagicMock(host="172.18.0.2")

    settings.TRUSTED_PROXY = True
    assert get_client_ip(req) == "198.51.100.42"
    settings.TRUSTED_PROXY = False


def test_distinct_remote_visitors_get_individual_rate_limit_buckets() -> None:
    """Two different client IPs receive separate rate limiter buckets."""
    rate_limiter.reset()
    rate_limiter.enabled = True

    ip_a = "203.0.113.10"
    ip_b = "203.0.113.20"
    email = "target@example.com"

    # Max out failures for ip_a (5 failures)
    for _ in range(5):
        rate_limiter.check_login_attempt(ip_a, email)
        rate_limiter.record_login_failure(ip_a, email)

    # Next attempt from ip_a is blocked
    with pytest.raises(RateLimitExceededException):
        rate_limiter.check_login_attempt(ip_a, email)

    # ip_b is unaffected and allowed to attempt
    rate_limiter.check_login_attempt(ip_b, email)

    rate_limiter.enabled = False
    rate_limiter.reset()
