"""Integration tests for user registration and automatic profile provisioning."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import SESSION_COOKIE_NAME
from app.models.organization_profile import OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import User


def test_register_student_and_organization(real_db_client: TestClient) -> None:
    # 1. Register student
    resp_student = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "student1@example.com",
            "password": "Password123!",
            "full_name": "Test Student",
            "role": "student",
        },
    )
    assert resp_student.status_code == 201
    data_student = resp_student.json()
    assert data_student["email"] == "student1@example.com"
    assert data_student["role"] == "student"
    assert "password_hash" not in data_student
    assert SESSION_COOKIE_NAME in resp_student.cookies

    # 2. Register organization
    resp_org = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "org1@example.com",
            "password": "Password123!",
            "full_name": "Acme Corp",
            "role": "organization",
            "organization_name": "Acme Corp",
        },
    )
    assert resp_org.status_code == 201
    data_org = resp_org.json()
    assert data_org["email"] == "org1@example.com"
    assert data_org["role"] == "organization"


def test_register_rejects_instructor_and_admin(real_db_client: TestClient) -> None:
    resp_instructor = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "instructor@example.com",
            "password": "Password123!",
            "full_name": "Instructor Name",
            "role": "instructor",
        },
    )
    assert resp_instructor.status_code == 422

    resp_admin = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "admin@example.com",
            "password": "Password123!",
            "full_name": "Admin Name",
            "role": "admin",
        },
    )
    assert resp_admin.status_code == 422


def test_register_duplicate_email(real_db_client: TestClient) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": "Password123!",
        "full_name": "First User",
        "role": "student",
    }
    resp1 = real_db_client.post("/api/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = real_db_client.post(
        "/api/auth/register",
        json={**payload, "full_name": "Second User"},
    )
    assert resp2.status_code == 409
    body = resp2.json()
    assert body["code"] == "EMAIL_ALREADY_REGISTERED"


def test_register_password_length_validation(real_db_client: TestClient) -> None:
    # Short password (< 8 chars)
    resp_short = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "short@example.com",
            "password": "short",
            "full_name": "Short Password",
            "role": "student",
        },
    )
    assert resp_short.status_code == 422

    # Long password (> 128 chars)
    resp_long = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "long@example.com",
            "password": "a" * 129,
            "full_name": "Long Password",
            "role": "student",
        },
    )
    assert resp_long.status_code == 422


def test_email_normalization(real_db_client: TestClient, real_db_session: Session) -> None:
    resp = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "  MixedCase.Student@Example.COM  ",
            "password": "Password123!",
            "full_name": "Normalized Student",
            "role": "student",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "mixedcase.student@example.com"

    # Verify directly in database
    user = real_db_session.scalar(select(User).where(User.email == "mixedcase.student@example.com"))
    assert user is not None
    assert user.email == "mixedcase.student@example.com"


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
