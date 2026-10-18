"""Integration tests for course creation permissions and validation."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_course_creation_instructor_only(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Instructors can create courses; students and organizations receive 403."""
    create_test_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    create_test_user(real_db_session, "stud@test.edu", UserRole.STUDENT)
    create_test_user(real_db_session, "org@test.edu", UserRole.ORGANIZATION)

    # Student -> 403
    login_test_user(real_db_client, "stud@test.edu")
    resp_student = real_db_client.post(
        "/api/courses",
        json={"title": "Data Structures", "description": "CS Course"},
    )
    assert resp_student.status_code == 403

    # Organization -> 403
    login_test_user(real_db_client, "org@test.edu")
    resp_org = real_db_client.post(
        "/api/courses",
        json={"title": "Data Structures", "description": "CS Course"},
    )
    assert resp_org.status_code == 403

    # Instructor -> 201
    login_test_user(real_db_client, "inst@test.edu")
    resp_inst = real_db_client.post(
        "/api/courses",
        json={"title": "Data Structures", "description": "CS Course"},
    )
    assert resp_inst.status_code == 201
    data = resp_inst.json()
    assert data["title"] == "Data Structures"
    assert data["status"] == "draft"
    assert data["instructor_name"] == "Test User"


def test_course_creation_rejects_extra_fields(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """A client can never send instructor_id or unknown fields."""
    create_test_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    login_test_user(real_db_client, "inst@test.edu")

    resp = real_db_client.post(
        "/api/courses",
        json={
            "title": "Machine Learning",
            "instructor_id": 999,
        },
    )
    assert resp.status_code == 422


def test_course_validation_rules(real_db_client: TestClient, real_db_session: Session) -> None:
    """Title must be 3-120 characters and description at most 2000."""
    create_test_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    login_test_user(real_db_client, "inst@test.edu")

    # Short title
    resp_short = real_db_client.post("/api/courses", json={"title": "ab"})
    assert resp_short.status_code == 422

    # Long title
    resp_long = real_db_client.post("/api/courses", json={"title": "a" * 121})
    assert resp_long.status_code == 422

    # Long description
    resp_desc = real_db_client.post(
        "/api/courses",
        json={"title": "Valid Title", "description": "d" * 2001},
    )
    assert resp_desc.status_code == 422
