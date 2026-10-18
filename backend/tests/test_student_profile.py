"""Integration tests for student profiles endpoints and validation rules."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student_profile import StudentProfile
from app.models.user import User


def _register_student(client: TestClient, email: str = "student@test.edu") -> dict[str, str]:
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


def _register_organization(client: TestClient, email: str = "org@test.edu") -> dict[str, str]:
    """Helper to register and authenticate an organization user."""
    resp = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "Password123!",
            "full_name": "Org Representative",
            "role": "organization",
            "organization_name": "Tech Corp",
        },
    )
    assert resp.status_code == 201
    return resp.json()


def test_get_own_student_profile_success(real_db_client: TestClient) -> None:
    user_data = _register_student(real_db_client)

    resp = real_db_client.get("/api/students/me")
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["user_id"] == user_data["id"]
    assert profile["university"] is None
    assert profile["department"] is None
    assert profile["year_of_study"] is None
    assert profile["bio"] is None
    assert profile["skills"] == []
    assert "updated_at" in profile


def test_update_own_student_profile_success(real_db_client: TestClient) -> None:
    user_data = _register_student(real_db_client)

    update_payload = {
        "university": "Stanford University",
        "department": "Computer Science",
        "year_of_study": 3,
        "bio": "Interested in distributed systems.",
        "skills": ["Python", "FastAPI", "PostgreSQL"],
    }

    put_resp = real_db_client.put("/api/students/me", json=update_payload)
    assert put_resp.status_code == 200
    updated = put_resp.json()
    assert updated["user_id"] == user_data["id"]
    assert updated["university"] == "Stanford University"
    assert updated["department"] == "Computer Science"
    assert updated["year_of_study"] == 3
    assert updated["bio"] == "Interested in distributed systems."
    assert updated["skills"] == ["Python", "FastAPI", "PostgreSQL"]

    # Verify persistence via GET
    get_resp = real_db_client.get("/api/students/me")
    assert get_resp.status_code == 200
    assert get_resp.json() == updated


def test_student_profile_other_role_gets_403(real_db_client: TestClient) -> None:
    _register_organization(real_db_client)

    get_resp = real_db_client.get("/api/students/me")
    assert get_resp.status_code == 403
    assert get_resp.json()["code"] == "FORBIDDEN"

    put_resp = real_db_client.put(
        "/api/students/me",
        json={"university": "Forbidden University"},
    )
    assert put_resp.status_code == 403
    assert put_resp.json()["code"] == "FORBIDDEN"


def test_student_profile_signed_out_gets_401(real_db_client: TestClient) -> None:
    get_resp = real_db_client.get("/api/students/me")
    assert get_resp.status_code == 401
    assert get_resp.json()["code"] == "UNAUTHORIZED"

    put_resp = real_db_client.put(
        "/api/students/me",
        json={"university": "Unauthorized University"},
    )
    assert put_resp.status_code == 401
    assert put_resp.json()["code"] == "UNAUTHORIZED"


def test_student_profile_user_id_in_body_is_rejected(real_db_client: TestClient) -> None:
    _register_student(real_db_client)

    resp = real_db_client.put(
        "/api/students/me",
        json={"user_id": 9999, "university": "MIT"},
    )
    assert resp.status_code == 422


def test_student_profile_unknown_fields_rejected(real_db_client: TestClient) -> None:
    _register_student(real_db_client)

    resp = real_db_client.put(
        "/api/students/me",
        json={"non_existent_field": "hacked"},
    )
    assert resp.status_code == 422


def test_student_profile_validation_rules(real_db_client: TestClient) -> None:
    _register_student(real_db_client)

    # year_of_study out of bounds
    assert real_db_client.put("/api/students/me", json={"year_of_study": 0}).status_code == 422
    assert real_db_client.put("/api/students/me", json={"year_of_study": 7}).status_code == 422

    # year_of_study valid values
    assert real_db_client.put("/api/students/me", json={"year_of_study": 1}).status_code == 200
    assert real_db_client.put("/api/students/me", json={"year_of_study": 6}).status_code == 200

    # bio max length 1000
    assert real_db_client.put("/api/students/me", json={"bio": "a" * 1001}).status_code == 422
    assert real_db_client.put("/api/students/me", json={"bio": "a" * 1000}).status_code == 200

    # skill over 40 chars
    assert real_db_client.put("/api/students/me", json={"skills": ["a" * 41]}).status_code == 422

    # max 20 skills
    assert (
        real_db_client.put(
            "/api/students/me",
            json={"skills": [f"skill-{i}" for i in range(21)]},
        ).status_code
        == 422
    )
    assert (
        real_db_client.put(
            "/api/students/me",
            json={"skills": [f"skill-{i}" for i in range(20)]},
        ).status_code
        == 200
    )

    # skills whitespace trimming and case-insensitive deduplication
    dedup_resp = real_db_client.put(
        "/api/students/me",
        json={"skills": ["  Python  ", "python", "PYTHON", "  FastAPI ", "FastAPI"]},
    )
    assert dedup_resp.status_code == 200
    assert dedup_resp.json()["skills"] == ["Python", "FastAPI"]

    # text fields whitespace trimmed and empty converted to None
    trim_resp = real_db_client.put(
        "/api/students/me",
        json={"university": "   Harvard   ", "department": "   "},
    )
    assert trim_resp.status_code == 200
    assert trim_resp.json()["university"] == "Harvard"
    assert trim_resp.json()["department"] is None


def test_updating_one_student_profile_never_changes_another(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    # Register student A
    _register_student(real_db_client, email="student_a@test.edu")
    put_a = real_db_client.put(
        "/api/students/me",
        json={"university": "MIT", "skills": ["Python"]},
    )
    assert put_a.status_code == 200

    # Logout and register student B
    real_db_client.post("/api/auth/logout")
    _register_student(real_db_client, email="student_b@test.edu")

    # Student B profile should be empty
    get_b = real_db_client.get("/api/students/me")
    assert get_b.status_code == 200
    assert get_b.json()["university"] is None
    assert get_b.json()["skills"] == []

    # Student B updates own profile
    put_b = real_db_client.put(
        "/api/students/me",
        json={"university": "Oxford", "skills": ["Go"]},
    )
    assert put_b.status_code == 200
    assert put_b.json()["university"] == "Oxford"

    # Verify directly in database that Student A's profile was not affected
    user_a = real_db_session.scalar(select(User).where(User.email == "student_a@test.edu"))
    assert user_a is not None
    profile_a = real_db_session.scalar(
        select(StudentProfile).where(StudentProfile.user_id == user_a.id)
    )
    assert profile_a is not None
    assert profile_a.university == "MIT"
    assert profile_a.skills == ["Python"]
