"""Tests for request logging, error handling, correlation ID, and secret leakage prevention."""

import logging
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.services.auth import AuthService


def test_unhandled_exception_returns_generic_500_with_request_id() -> None:
    """Unhandled exceptions return a generic 500 JSON payload with request_id and no traceback."""
    with (
        TestClient(app, raise_server_exceptions=False) as client,
        patch.object(
            AuthService, "authenticate", side_effect=ZeroDivisionError("Unexpected math crash")
        ),
    ):
        resp = client.post(
            "/api/auth/login",
            json={"email": "crash@example.com", "password": "Password123!"},
        )

    assert resp.status_code == 500
    data = resp.json()
    assert data["code"] == "INTERNAL_SERVER_ERROR"
    assert data["detail"] == "An internal server error occurred."
    assert "request_id" in data
    assert len(data["request_id"]) > 0

    # Guarantee no internal stack trace or exception class is leaked
    raw_response_text = resp.text
    assert "ZeroDivisionError" not in raw_response_text
    assert "Unexpected math crash" not in raw_response_text
    assert "Traceback" not in raw_response_text


def test_response_contains_x_request_id_header(client: TestClient) -> None:
    """Every response includes an X-Request-ID correlation header."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert "X-Request-ID" in resp.headers
    assert len(resp.headers["X-Request-ID"]) > 0


def test_logs_contain_safe_metadata_and_no_secrets(client: TestClient) -> None:
    """Logs capture request_id, method, path, status, duration and NEVER passwords or tokens."""
    from app.core.logging import logger

    captured: list[str] = []

    class MemoryHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            captured.append(record.getMessage())

    handler = MemoryHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.disabled = False

    secret_password = "SuperSecretPassword999!"
    secret_token = "secret_session_token_xyz123"
    secret_body_val = "classified_private_data"

    try:
        # 1. Login attempt with sensitive password
        client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": secret_password},
        )

        # 2. Authenticated-style request with secret session cookie and header
        client.get(
            "/api/auth/me",
            headers={
                "Cookie": f"session_token={secret_token}",
                "Authorization": f"Bearer {secret_token}",
            },
        )

        # 3. Registration with sensitive body
        client.post(
            "/api/auth/register",
            json={
                "email": "user.logtest@example.com",
                "password": secret_password,
                "full_name": secret_body_val,
                "role": "student",
            },
        )

        assert len(captured) >= 3

        for msg in captured:
            assert "request_id=" in msg
            assert "method=" in msg
            assert "path=" in msg
            assert "status=" in msg
            assert "duration_ms=" in msg

            # Strict secrecy assertions: secrets must never leak into any log record
            assert secret_password not in msg
            assert secret_token not in msg
            assert secret_body_val not in msg
            assert "password" not in msg.lower() or "password_hash" in msg.lower()
    finally:
        logger.removeHandler(handler)


def test_database_connection_error_returns_503_with_request_id() -> None:
    """Database connection errors return a 503 JSON payload with request_id."""
    from sqlalchemy.exc import OperationalError

    err = OperationalError("could not connect to server: Connection refused", None, None)
    with (
        TestClient(app, raise_server_exceptions=False) as client,
        patch.object(AuthService, "authenticate", side_effect=err),
    ):
        resp = client.post(
            "/api/auth/login",
            json={"email": "dbfail@example.com", "password": "Password123!"},
        )

    assert resp.status_code == 503
    data = resp.json()
    assert data["code"] == "DATABASE_UNAVAILABLE"
    assert data["detail"] == "Database service is temporarily unavailable. Please try again later."
    assert "request_id" in data
    assert len(data["request_id"]) > 0
    assert resp.headers.get("X-Request-ID") == data["request_id"]
