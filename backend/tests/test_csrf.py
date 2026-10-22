"""Tests for Cross-Site Request Forgery (CSRF) origin and referer defence."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("method", ["POST", "PUT", "PATCH", "DELETE"])
def test_csrf_blocks_untrusted_origin(client: TestClient, method: str) -> None:
    """State-changing requests with untrusted Origin header receive 403 CSRF_FORBIDDEN."""
    resp = client.request(
        method=method,
        url="/api/auth/login",
        headers={"Origin": "https://attacker.example.com"},
    )
    assert resp.status_code == 403
    data = resp.json()
    assert data["code"] == "CSRF_FORBIDDEN"
    assert "Cross-origin request forbidden" in data["detail"]


def test_csrf_allows_vite_dev_origin(client: TestClient) -> None:
    """Requests with Vite dev origin (http://localhost:5173) are allowed through."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "wrongpassword123"},
        headers={"Origin": "http://localhost:5173"},
    )
    # Reaches auth service and returns 401 instead of 403
    assert resp.status_code == 401


def test_csrf_allows_allowed_secondary_origin(client: TestClient) -> None:
    """Requests with secondary allowed origin (http://localhost:3000) are allowed through."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "wrongpassword123"},
        headers={"Origin": "http://localhost:3000"},
    )
    assert resp.status_code == 401


def test_csrf_fallback_to_referer_blocks_untrusted(client: TestClient) -> None:
    """When Origin is absent, an untrusted Referer header receives 403."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "wrongpassword123"},
        headers={"Referer": "https://malicious-site.com/exploit"},
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "CSRF_FORBIDDEN"


def test_csrf_fallback_to_referer_allows_trusted(client: TestClient) -> None:
    """When Origin is absent, a trusted Referer header is allowed through."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "wrongpassword123"},
        headers={"Referer": "http://localhost:5173/auth/login"},
    )
    assert resp.status_code == 401


def test_csrf_allows_non_browser_clients_without_origin_or_referer(
    client: TestClient,
) -> None:
    """Non-browser requests without Origin and Referer headers are allowed through."""
    resp = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "wrongpassword123"},
    )
    assert resp.status_code == 401


def test_csrf_allows_safe_methods_with_any_origin(client: TestClient) -> None:
    """Safe methods (GET, HEAD, OPTIONS) do not trigger CSRF rejection."""
    resp = client.get("/api/health", headers={"Origin": "https://attacker.example.com"})
    assert resp.status_code == 200
