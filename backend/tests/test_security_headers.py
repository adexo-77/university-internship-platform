"""Tests for security headers middleware."""

from fastapi.testclient import TestClient


def test_global_security_headers_present_on_all_responses(client: TestClient) -> None:
    """Every response includes required browser defensive headers."""
    resp = client.get("/api/health")
    assert resp.status_code == 200

    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"
    assert resp.headers.get("Permissions-Policy") == ("camera=(), microphone=(), geolocation=()")


def test_cache_control_no_store_on_auth_responses(client: TestClient) -> None:
    """Responses under /api/auth include Cache-Control: no-store."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "wrong"},
    )
    assert resp.headers.get("Cache-Control") == "no-store"
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"


def test_cache_control_no_store_on_dashboard_responses(client: TestClient) -> None:
    """Responses under /api/dashboard include Cache-Control: no-store."""
    resp = client.get("/api/dashboard/student")
    assert resp.headers.get("Cache-Control") == "no-store"
    assert resp.headers.get("X-Frame-Options") == "DENY"


def test_cache_control_not_forced_on_public_health(client: TestClient) -> None:
    """Public endpoints such as health check do not force Cache-Control: no-store."""
    resp = client.get("/api/health")
    assert resp.headers.get("Cache-Control") != "no-store"
