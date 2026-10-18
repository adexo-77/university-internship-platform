"""Integration tests for organization profiles endpoints and validation rules."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization_profile import OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import User


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


def test_update_own_organization_profile_success(real_db_client: TestClient) -> None:
    user_data = _register_organization(real_db_client)

    update_payload = {
        "organization_name": "Acme Global Solutions",
        "industry": "Software Engineering",
        "location": "Nairobi, Kenya",
        "website": "https://acme.example.com",
        "description": "Building sustainable enterprise tools.",
    }

    put_resp = real_db_client.put("/api/organizations/me", json=update_payload)
    assert put_resp.status_code == 200
    updated = put_resp.json()
    assert updated["user_id"] == user_data["id"]
    assert updated["organization_name"] == "Acme Global Solutions"
    assert updated["industry"] == "Software Engineering"
    assert updated["location"] == "Nairobi, Kenya"
    assert updated["website"] == "https://acme.example.com"
    assert updated["description"] == "Building sustainable enterprise tools."

    # Verify persistence via GET
    get_resp = real_db_client.get("/api/organizations/me")
    assert get_resp.status_code == 200
    assert get_resp.json() == updated


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


def test_organization_profile_validation_rules(real_db_client: TestClient) -> None:
    _register_organization(real_db_client)

    # Empty organization_name rejected
    assert (
        real_db_client.put("/api/organizations/me", json={"organization_name": ""}).status_code
        == 422
    )
    assert (
        real_db_client.put("/api/organizations/me", json={"organization_name": "   "}).status_code
        == 422
    )

    # Website validation: invalid scheme / format
    assert (
        real_db_client.put(
            "/api/organizations/me",
            json={"organization_name": "Acme", "website": "not-a-url"},
        ).status_code
        == 422
    )
    assert (
        real_db_client.put(
            "/api/organizations/me",
            json={"organization_name": "Acme", "website": "ftp://files.example.com"},
        ).status_code
        == 422
    )
    assert (
        real_db_client.put(
            "/api/organizations/me",
            json={"organization_name": "Acme", "website": "http://"},
        ).status_code
        == 422
    )

    # Website validation: valid URLs
    assert (
        real_db_client.put(
            "/api/organizations/me",
            json={"organization_name": "Acme", "website": "https://example.com/company"},
        ).status_code
        == 200
    )
    assert (
        real_db_client.put(
            "/api/organizations/me",
            json={"organization_name": "Acme", "website": "http://localhost:3000"},
        ).status_code
        == 200
    )

    # Description max length 1000
    assert (
        real_db_client.put(
            "/api/organizations/me",
            json={"organization_name": "Acme", "description": "a" * 1001},
        ).status_code
        == 422
    )
    assert (
        real_db_client.put(
            "/api/organizations/me",
            json={"organization_name": "Acme", "description": "a" * 1000},
        ).status_code
        == 200
    )

    # Whitespace trimming
    trim_resp = real_db_client.put(
        "/api/organizations/me",
        json={
            "organization_name": "  Trimmed Name  ",
            "industry": "   Fintech   ",
            "location": "   ",
        },
    )
    assert trim_resp.status_code == 200
    assert trim_resp.json()["organization_name"] == "Trimmed Name"
    assert trim_resp.json()["industry"] == "Fintech"
    assert trim_resp.json()["location"] is None


def test_updating_one_organization_profile_never_changes_another(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    # Register Org A
    _register_organization(real_db_client, email="org_a@test.com", org_name="Org A")
    put_a = real_db_client.put(
        "/api/organizations/me",
        json={"organization_name": "Org A Updated", "industry": "Energy"},
    )
    assert put_a.status_code == 200

    # Logout and register Org B
    real_db_client.post("/api/auth/logout")
    _register_organization(real_db_client, email="org_b@test.com", org_name="Org B")

    # Org B updates own profile
    put_b = real_db_client.put(
        "/api/organizations/me",
        json={"organization_name": "Org B Updated", "industry": "Healthcare"},
    )
    assert put_b.status_code == 200

    # Verify directly in database that Org A was not modified
    user_a = real_db_session.scalar(select(User).where(User.email == "org_a@test.com"))
    assert user_a is not None
    profile_a = real_db_session.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == user_a.id)
    )
    assert profile_a is not None
    assert profile_a.organization_name == "Org A Updated"
    assert profile_a.industry == "Energy"


def test_registration_creates_profile_row_and_atomic_failure(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    # 1. Student registration creates empty student profile row in same transaction
    student_resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "auto_student@test.com",
            "password": "Password123!",
            "full_name": "Auto Student",
            "role": "student",
        },
    )
    assert student_resp.status_code == 201
    student_user = real_db_session.scalar(select(User).where(User.email == "auto_student@test.com"))
    assert student_user is not None
    sp = real_db_session.scalar(
        select(StudentProfile).where(StudentProfile.user_id == student_user.id)
    )
    assert sp is not None
    assert sp.skills == []

    # 2. Organization registration creates profile with organization_name in same transaction
    org_resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "auto_org@test.com",
            "password": "Password123!",
            "full_name": "Auto Org Rep",
            "role": "organization",
            "organization_name": "Quantum Labs",
        },
    )
    assert org_resp.status_code == 201
    org_user = real_db_session.scalar(select(User).where(User.email == "auto_org@test.com"))
    assert org_user is not None
    op = real_db_session.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == org_user.id)
    )
    assert op is not None
    assert op.organization_name == "Quantum Labs"

    # 3. Organization registration without organization_name fails and creates NO user
    missing_name_resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "fail_org@test.com",
            "password": "Password123!",
            "full_name": "Fail Org Rep",
            "role": "organization",
        },
    )
    assert missing_name_resp.status_code == 422
    uncreated_user = real_db_session.scalar(select(User).where(User.email == "fail_org@test.com"))
    assert uncreated_user is None
