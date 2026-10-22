"""Authorization sweep verifying universal authentication and strict admin RBAC enforcement."""

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

        # Substitute route path parameters like {id} or {user_id} with dummy identifier '1'
        concrete_path = re.sub(r"\{[^}]+\}", "1", path)

        for method in path_item:
            if method.lower() in ("head", "options"):
                continue

            resp = client.request(method.upper(), concrete_path)
            assert resp.status_code == 401, (
                f"Route [{method.upper()} {path}] is not public but returned "
                f"status {resp.status_code} without session authentication."
            )


@pytest.mark.parametrize(
    "role",
    [UserRole.STUDENT, UserRole.INSTRUCTOR, UserRole.ORGANIZATION],
)
def test_admin_routes_return_403_for_non_admin_roles(
    real_db_client: TestClient,
    real_db_session: Session,
    role: UserRole,
) -> None:
    """Every /api/admin route returns 403 Forbidden for student, instructor, and organization."""
    email = f"sweep_{role.value}@example.com"
    pwd = "ValidPassword123!"
    create_test_user(db=real_db_session, email=email, role=role, password=pwd)

    # Log in as the non-admin user
    login_resp = real_db_client.post("/api/auth/login", json={"email": email, "password": pwd})
    assert login_resp.status_code == 200

    openapi_schema = app.openapi()
    admin_paths = [p for p in openapi_schema.get("paths", {}) if p.startswith("/api/admin")]
    assert len(admin_paths) > 0, "There must be /api/admin routes registered"

    for path in admin_paths:
        concrete_path = re.sub(r"\{[^}]+\}", "1", path)
        for method in openapi_schema["paths"][path]:
            if method.lower() in ("head", "options"):
                continue

            resp = real_db_client.request(method.upper(), concrete_path)
            assert resp.status_code == 403, (
                f"Admin route [{method.upper()} {path}] failed to block role '{role.value}' "
                f"(returned status {resp.status_code} instead of 403 Forbidden)."
            )
