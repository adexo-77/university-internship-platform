"""Tests for request size limits, sanitization, unicode normalization, and error resilience."""

import pytest
from fastapi.testclient import TestClient


def test_request_body_size_limit_returns_413(client: TestClient) -> None:
    """Payloads exceeding 256 KB receive 413 with PAYLOAD_TOO_LARGE."""
    oversized_data = "a" * (260 * 1024)  # 260 KB
    resp = client.post(
        "/api/auth/login",
        json={"email": "user@example.com", "password": oversized_data},
    )
    assert resp.status_code == 413
    assert resp.json()["code"] == "PAYLOAD_TOO_LARGE"


def test_null_bytes_rejected_in_auth_endpoints(client: TestClient) -> None:
    """Null bytes in login, register, and change-password return 422, never 500."""
    # Register with null bytes
    resp_reg = client.post(
        "/api/auth/register",
        json={
            "email": "test\x00@example.com",
            "password": "Password123!",
            "full_name": "Test User",
            "role": "student",
        },
    )
    assert resp_reg.status_code == 422

    # Login with null byte in email (reproduces previous unhandled driver error)
    resp_login_email = client.post(
        "/api/auth/login",
        json={"email": "attacker\x00@example.com", "password": "Password123!"},
    )
    assert resp_login_email.status_code == 422

    # Login with null byte in password
    resp_login_pwd = client.post(
        "/api/auth/login",
        json={"email": "attacker@example.com", "password": "pass\x00word123"},
    )
    assert resp_login_pwd.status_code == 422


def test_control_characters_rejected_in_auth(client: TestClient) -> None:
    """ASCII control characters in text fields return 422."""
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "bad\x07name@example.com",
            "password": "Password123!",
            "full_name": "Bad\x1fName",
            "role": "student",
        },
    )
    assert resp.status_code == 422


def test_unicode_email_safe_normalization(real_db_client: TestClient) -> None:
    """Unicode emails are normalized using NFKC safely and handle case folding."""
    reg_resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "STUDENT.UNİCODE@EXAMPLE.COM",
            "password": "Password123!",
            "full_name": "Unicode Student",
            "role": "student",
        },
    )
    assert reg_resp.status_code == 201

    login_resp = real_db_client.post(
        "/api/auth/login",
        json={
            "email": "student.unıcode@example.com",
            "password": "Password123!",
        },
    )
    assert login_resp.status_code in (200, 401)
    assert login_resp.status_code != 500


@pytest.mark.parametrize(
    "malformed_payload",
    [
        {},  # empty
        {"email": "", "password": ""},  # blank strings
        {"email": 12345, "password": ["invalid"]},  # wrong types
        {"email": "null\x00@test.com", "password": "pwd"},  # null byte
        {"email": "test@example.com", "password": "a" * (260 * 1024)},  # oversized
        {"email": "unclosed_quotes'", "password": 999},  # malformed syntax
    ],
)
def test_login_never_returns_500(client: TestClient, malformed_payload: dict) -> None:
    """Login never returns 500 for malformed, empty, wrongly typed, or oversized input."""
    resp = client.post("/api/auth/login", json=malformed_payload)
    assert resp.status_code in (401, 413, 422)
    assert resp.status_code != 500


@pytest.mark.parametrize(
    "malformed_payload",
    [
        {},
        {"email": None, "password": None, "full_name": None, "role": None},
        {"email": 999, "password": False, "full_name": {}, "role": "invalid"},
        {"email": "test\x00@example.com", "password": "ValidPassword123!", "full_name": "Nul"},
        {"email": "a" * 1000, "password": "a" * (260 * 1024)},
    ],
)
def test_register_never_returns_500(client: TestClient, malformed_payload: dict) -> None:
    """Register never returns 500 for malformed, empty, wrongly typed, or oversized input."""
    resp = client.post("/api/auth/register", json=malformed_payload)
    assert resp.status_code in (413, 422)
    assert resp.status_code != 500


@pytest.mark.parametrize(
    "malformed_payload",
    [
        {},
        {"current_password": "", "new_password": ""},
        {"current_password": 12345, "new_password": ["abc"]},
        {"current_password": "valid\x00pwd", "new_password": "NewPassword123!"},
        {"current_password": "pwd", "new_password": "x" * (260 * 1024)},
    ],
)
def test_change_password_never_returns_500(
    real_db_client: TestClient,
    malformed_payload: dict,
) -> None:
    """Change-password never returns 500 for malformed, empty, or oversized input."""
    resp = real_db_client.post("/api/auth/change-password", json=malformed_payload)
    assert resp.status_code in (401, 413, 422)
    assert resp.status_code != 500
