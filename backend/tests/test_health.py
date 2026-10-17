"""Tests for system and database health endpoints mounted under /api."""

from fastapi.testclient import TestClient

from app.core.config import settings


def test_api_health_returns_status_ok(client: TestClient) -> None:
    """GET /api/health must return status 200 and {'status': 'ok'}."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_health_not_mounted(client: TestClient) -> None:
    """GET /health must return status 404 since routes are mounted under /api only."""
    response = client.get("/health")
    assert response.status_code == 404


def test_api_health_db_with_real_database(real_db_client: TestClient) -> None:
    """GET /api/health/db must execute SELECT 1 against the real database from TEST_DATABASE_URL."""
    response = real_db_client.get("/api/health/db")
    assert response.status_code == 200
    assert response.json() == {"database": "ok"}


def test_api_health_db_returns_clear_error_when_database_fails(
    client_with_failing_db: TestClient,
) -> None:
    """GET /api/health/db must return status 503 with a clear error when DB is unavailable."""
    response = client_with_failing_db.get("/api/health/db")
    assert response.status_code == 503
    payload = response.json()
    assert "detail" in payload
    assert "Database connection error" in payload["detail"]


def test_settings_loaded_properly() -> None:
    """Ensure settings are loaded with valid defaults and no hardcoded paths."""
    assert settings.PORT == 8001
    assert "postgresql" in settings.DATABASE_URL
    assert "postgresql" in settings.TEST_DATABASE_URL
    assert not any("\\" in origin for origin in settings.CORS_ORIGINS)
