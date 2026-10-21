"""Integration tests for student dashboard role guards and empty states."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import UserRole
from tests.factories import (
    create_test_student,
    create_test_user,
    login_test_user,
)


def test_student_dashboard_role_guards(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Only authenticated students may access the student dashboard."""
    real_db_client.cookies.clear()
    assert real_db_client.get("/api/dashboard/student").status_code == 401

    for role in [UserRole.INSTRUCTOR, UserRole.ORGANIZATION, UserRole.ADMIN]:
        u = create_test_user(real_db_session, f"guard_{role.value}@test.com", role)
        login_test_user(real_db_client, u.email)
        assert real_db_client.get("/api/dashboard/student").status_code == 403

    student, _ = create_test_student(real_db_session, "guard_student@test.com")
    login_test_user(real_db_client, student.email)
    assert real_db_client.get("/api/dashboard/student").status_code == 200


def test_student_dashboard_empty_state(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Empty student account returns empty lists, zero progress, and false profile completeness."""
    student = create_test_user(real_db_session, "empty_student@test.com", UserRole.STUDENT)
    login_test_user(real_db_client, student.email)

    resp = real_db_client.get("/api/dashboard/student")
    assert resp.status_code == 200
    data = resp.json()

    assert data["due_next"] == []
    assert data["recent_grades"] == []
    assert data["courses"] == []
    assert data["profile_complete"] is False
    assert data["applications"]["recent"] == []
    for count in data["applications"]["counts_by_status"].values():
        assert count == 0
