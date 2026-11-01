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


def test_hsts_sent_only_over_https(client: TestClient) -> None:
    """Strict-Transport-Security header is sent exclusively on HTTPS requests."""
    from app.core.config import settings

    # Plain HTTP: no HSTS
    resp_http = client.get("/api/health")
    assert "Strict-Transport-Security" not in resp_http.headers

    # HTTPS via trusted reverse proxy / tunnel: HSTS header is present
    settings.TRUSTED_PROXY = True
    try:
        resp_https = client.get(
            "/api/health",
            headers={"X-Forwarded-Proto": "https"},
        )
        assert resp_https.headers.get("Strict-Transport-Security") == (
            "max-age=31536000; includeSubDomains"
        )

        # HTTP via trusted reverse proxy: no HSTS
        resp_proxy_http = client.get(
            "/api/health",
            headers={"X-Forwarded-Proto": "http"},
        )
        assert "Strict-Transport-Security" not in resp_proxy_http.headers
    finally:
        settings.TRUSTED_PROXY = False
