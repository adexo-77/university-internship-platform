"""Integration tests for administrator user management and search."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_admin_user_endpoints_role_guards(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Every admin endpoint returns 401 when signed out and 403 for non-admins."""
    endpoints = [
        ("GET", "/api/admin/users", None),
        (
            "POST",
            "/api/admin/users",
            {
                "email": "u@brolf.com",
                "password": "Password123!",
                "full_name": "U",
                "role": "instructor",
            },
        ),
        ("PATCH", "/api/admin/users/1", {"is_active": False}),
        ("PUT", "/api/admin/users/1/password", {"password": "NewPassword123!"}),
    ]

    for method, url, payload in endpoints:
        real_db_client.cookies.clear()
        resp = real_db_client.request(method, url, json=payload)
        assert resp.status_code == 401, f"{method} {url} should be 401 signed out"

    roles = [UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORGANIZATION]
    for role in roles:
        user = create_test_user(real_db_session, email=f"user_{role.value}@example.com", role=role)
        login_test_user(real_db_client, user.email)
        for method, url, payload in endpoints:
            resp = real_db_client.request(method, url, json=payload)
            assert resp.status_code == 403, f"{method} {url} should be 403 for {role.value}"


def test_admin_list_users_search_filter_and_pagination(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Admin can search users, filter by role and active status, and paginate."""
    admin = create_test_user(
        real_db_session, email="admin1@example.com", role=UserRole.ADMIN, full_name="Super Admin"
    )
    u1 = create_test_user(
        real_db_session,
        email="alice_inst@example.com",
        role=UserRole.INSTRUCTOR,
        full_name="Alice Instructor",
    )
    u2 = create_test_user(
        real_db_session,
        email="bob_student@example.com",
        role=UserRole.STUDENT,
        full_name="Bob Student",
    )
    u2.is_active = False
    real_db_session.commit()

    login_test_user(real_db_client, admin.email)

    resp = real_db_client.get("/api/admin/users")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data and "total" in data
    assert data["total"] >= 3

    # Password hash must NEVER appear
    for item in data["items"]:
        assert "password" not in item
        assert "password_hash" not in item

    # Search by query
    resp_q = real_db_client.get("/api/admin/users?q=alice")
    assert resp_q.status_code == 200
    items_q = resp_q.json()["items"]
    assert any(i["email"] == u1.email for i in items_q)
    assert not any(i["email"] == u2.email for i in items_q)

    # Filter by role
    resp_role = real_db_client.get("/api/admin/users?role=instructor")
    assert resp_role.status_code == 200
    for i in resp_role.json()["items"]:
        assert i["role"] == "instructor"

    # Filter by is_active
    resp_active = real_db_client.get("/api/admin/users?is_active=false")
    assert resp_active.status_code == 200
    assert any(i["email"] == u2.email for i in resp_active.json()["items"])
    assert not any(i["email"] == u1.email for i in resp_active.json()["items"])


def test_admin_create_instructor_and_admin_success(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Admin can provision instructor and admin accounts with email normalization."""
    admin = create_test_user(real_db_session, email="admin_prov@example.com", role=UserRole.ADMIN)
    login_test_user(real_db_client, admin.email)

    # Create instructor with mixed-case and whitespace email
    inst_payload = {
        "email": "  New.Instructor@University.Edu  ",
        "password": "Password123!",
        "full_name": "Dr. Sarah Connor",
        "role": "instructor",
    }
    resp = real_db_client.post("/api/admin/users", json=inst_payload)
    assert resp.status_code == 201
    inst_data = resp.json()
    assert inst_data["email"] == "new.instructor@university.edu"
    assert inst_data["role"] == "instructor"
    assert inst_data["full_name"] == "Dr. Sarah Connor"
    assert inst_data["is_active"] is True
    assert "password_hash" not in inst_data

    # Create admin
    admin_payload = {
        "email": "Second.Admin@university.edu",
        "password": "Password123!",
        "full_name": "Second Administrator",
        "role": "admin",
    }
    resp_admin = real_db_client.post("/api/admin/users", json=admin_payload)
    assert resp_admin.status_code == 201
    assert resp_admin.json()["role"] == "admin"


def test_admin_create_user_role_rejection_and_duplicates(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Creating student or organization via admin endpoint is rejected; duplicates return 409."""
    admin = create_test_user(real_db_session, email="admin_val@example.com", role=UserRole.ADMIN)
    login_test_user(real_db_client, admin.email)

    # Reject student role
    resp_student = real_db_client.post(
        "/api/admin/users",
        json={
            "email": "st@test.com",
            "password": "Password123!",
            "full_name": "S",
            "role": "student",
        },
    )
    assert resp_student.status_code == 422

    # Reject organization role
    resp_org = real_db_client.post(
        "/api/admin/users",
        json={
            "email": "org@test.com",
            "password": "Password123!",
            "full_name": "O",
            "role": "organization",
        },
    )
    assert resp_org.status_code == 422

    # Reject extra fields
    resp_extra = real_db_client.post(
        "/api/admin/users",
        json={
            "email": "extra@test.com",
            "password": "Password123!",
            "full_name": "E",
            "role": "instructor",
            "is_active": False,
        },
    )
    assert resp_extra.status_code == 422

    # Duplicate email returns 409
    create_test_user(real_db_session, email="existing@example.com", role=UserRole.INSTRUCTOR)
    resp_dup = real_db_client.post(
        "/api/admin/users",
        json={
            "email": "EXISTING@example.com",
            "password": "Password123!",
            "full_name": "Dupe",
            "role": "instructor",
        },
    )
    assert resp_dup.status_code == 409
