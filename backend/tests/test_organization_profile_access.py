"""Integration tests for organization profile access control and field guards."""

from fastapi.testclient import TestClient


def _register_organization(
    client: TestClient,
    email: str = "org@test.com",
    org_name: str = "Acme Technologies",
) -> dict[str, str]:
    """Helper to register and authenticate an organization user."""
    resp = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Org Admin",
            "role": "organization",
            "organization_name": org_name,
        },
    )
    assert resp.status_code == 201
    return resp.json()


def _register_student(client: TestClient, email: str = "student@test.com") -> dict[str, str]:
    """Helper to register and authenticate a student user."""
    resp = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Test Student",
            "role": "student",
        },
    )
    assert resp.status_code == 201
    return resp.json()


def test_get_own_organization_profile_success(real_db_client: TestClient) -> None:
    user_data = _register_organization(
        real_db_client,
        email="getorg@test.com",
        org_name="Innovate Corp",
    )

    resp = real_db_client.get("/api/organizations/me")
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["user_id"] == user_data["id"]
    assert profile["organization_name"] == "Innovate Corp"
    assert profile["industry"] is None
    assert profile["location"] is None
    assert profile["website"] is None
    assert profile["description"] is None
    assert "updated_at" in profile


def test_organization_profile_other_role_gets_403(real_db_client: TestClient) -> None:
    _register_student(real_db_client)

    get_resp = real_db_client.get("/api/organizations/me")
    assert get_resp.status_code == 403
    assert get_resp.json()["code"] == "FORBIDDEN"

    put_resp = real_db_client.put(
        "/api/organizations/me",
        json={"organization_name": "Hacked Org"},
    )
    assert put_resp.status_code == 403
    assert put_resp.json()["code"] == "FORBIDDEN"


def test_organization_profile_signed_out_gets_401(real_db_client: TestClient) -> None:
    get_resp = real_db_client.get("/api/organizations/me")
    assert get_resp.status_code == 401
    assert get_resp.json()["code"] == "UNAUTHORIZED"

    put_resp = real_db_client.put(
        "/api/organizations/me",
        json={"organization_name": "Unauthorized Org"},
    )
    assert put_resp.status_code == 401
    assert put_resp.json()["code"] == "UNAUTHORIZED"


def test_organization_profile_user_id_in_body_is_rejected(real_db_client: TestClient) -> None:
    _register_organization(real_db_client)

    resp = real_db_client.put(
        "/api/organizations/me",
        json={"user_id": 9999, "organization_name": "Spoofed ID"},
    )
    assert resp.status_code == 422


def test_organization_profile_unknown_fields_rejected(real_db_client: TestClient) -> None:
    _register_organization(real_db_client)

    resp = real_db_client.put(
        "/api/organizations/me",
        json={"organization_name": "Valid Org", "arbitrary_field": "disallowed"},
    )
    assert resp.status_code == 422
