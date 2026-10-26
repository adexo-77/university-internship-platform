"""Authorization sweep verifying universal authentication and role-matrix enforcement."""

import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.user import UserRole
from tests.factories import create_test_user

PUBLIC_ALLOWLIST = frozenset(
    {
        "/api/health",
        "/api/health/db",
        "/api/auth/register",
        "/api/auth/login",
        "/api/auth/logout",
    }
)

ALL_ROLES = frozenset(
    {
        UserRole.STUDENT,
        UserRole.INSTRUCTOR,
        UserRole.ORGANIZATION,
        UserRole.COORDINATOR,
        UserRole.ADMIN,
    }
)

# Role matrix: (HTTP method, route path template, allowed roles set)
ROLE_MATRIX: list[tuple[str, str, set[UserRole]]] = [
    # Admin-only user management
    ("GET", "/api/admin/users", {UserRole.ADMIN}),
    ("POST", "/api/admin/users", {UserRole.ADMIN}),
    ("PATCH", "/api/admin/users/1", {UserRole.ADMIN}),
    ("PUT", "/api/admin/users/1/password", {UserRole.ADMIN}),
    # Organization approval (admin and coordinator)
    ("GET", "/api/admin/organizations", {UserRole.ADMIN, UserRole.COORDINATOR}),
    ("PUT", "/api/admin/organizations/1/approval", {UserRole.ADMIN, UserRole.COORDINATOR}),
    # Internship review (admin and coordinator)
    ("GET", "/api/admin/internships", {UserRole.ADMIN, UserRole.COORDINATOR}),
    ("PUT", "/api/admin/internships/1/review", {UserRole.ADMIN, UserRole.COORDINATOR}),
    # Course management
    ("POST", "/api/courses", {UserRole.INSTRUCTOR}),
    ("PATCH", "/api/courses/1", {UserRole.INSTRUCTOR, UserRole.ADMIN}),
    # Internship management and applicant roster
    ("POST", "/api/internships", {UserRole.ORGANIZATION}),
    (
        "GET",
        "/api/internships/1/applications",
        {UserRole.ORGANIZATION, UserRole.ADMIN, UserRole.COORDINATOR},
    ),
    # Role-specific dashboards
    ("GET", "/api/dashboard/coordinator", {UserRole.COORDINATOR}),
    ("GET", "/api/dashboard/admin", {UserRole.ADMIN}),
    ("GET", "/api/dashboard/student", {UserRole.STUDENT}),
    ("GET", "/api/dashboard/instructor", {UserRole.INSTRUCTOR}),
    ("GET", "/api/dashboard/organization", {UserRole.ORGANIZATION}),
    # Achievement badges
    ("GET", "/api/students/me/badges", {UserRole.STUDENT}),
    # Administrative and coordinator CSV reports
    (
        "GET",
        "/api/admin/reports/applications.csv",
        {UserRole.ADMIN, UserRole.COORDINATOR},
    ),
    ("GET", "/api/admin/reports/users.csv", {UserRole.ADMIN}),
]


def test_authorization_sweep_all_routes_require_session_unless_public(
    client: TestClient,
) -> None:
    """Every registered route requires authentication (401) unless on explicit public allowlist."""
    openapi_schema = app.openapi()
    paths: dict = openapi_schema.get("paths", {})
    assert len(paths) > 0, "OpenAPI schema must contain registered paths"

    for path, path_item in paths.items():
        if path in PUBLIC_ALLOWLIST:
            continue

        concrete_path = re.sub(r"\{[^}]+\}", "1", path)
        for method in path_item:
            if method.lower() in ("head", "options"):
                continue

            resp = client.request(method.upper(), concrete_path)
            assert resp.status_code == 401, (
                f"Route [{method.upper()} {path}] is not public but returned "
                f"status {resp.status_code} without session authentication."
            )


@pytest.mark.parametrize("method,path,allowed_roles", ROLE_MATRIX)
def test_role_matrix_asserts_401_for_anonymous_users(
    client: TestClient,
    method: str,
    path: str,
    allowed_roles: set[UserRole],
) -> None:
    """Role matrix routes return 401 for unauthenticated anonymous users."""
    assert len(allowed_roles) > 0
    resp = client.request(method, path)
    assert resp.status_code == 401, (
        f"Route [{method} {path}] expected 401 for anonymous request, got {resp.status_code}."
    )


@pytest.mark.parametrize("role", sorted(ALL_ROLES, key=lambda r: r.value))
def test_role_matrix_authorization_sweep(
    real_db_client: TestClient,
    real_db_session: Session,
    role: UserRole,
) -> None:
    """Every route in the role matrix asserts 403 for disallowed roles and allows authorized."""
    email = f"sweep_matrix_{role.value}@example.com"
    pwd = "ValidPassword123!"
    create_test_user(db=real_db_session, email=email, role=role, password=pwd)

    login_resp = real_db_client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert login_resp.status_code == 200

    for method, path, allowed_roles in ROLE_MATRIX:
        resp = real_db_client.request(method, path)
        if role not in allowed_roles:
            assert resp.status_code == 403, (
                f"Route [{method} {path}] failed to block disallowed role '{role.value}' "
                f"(status {resp.status_code} != 403)."
            )
        else:
            assert resp.status_code != 403, (
                f"Route [{method} {path}] unexpectedly returned 403 for role '{role.value}'."
            )
