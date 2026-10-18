"""Integration tests for course updates and status transitions."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.course import Course, CourseStatus
from app.models.user import UserRole
from tests.conftest import create_test_user, login_test_user


def test_course_update_and_status_transition_rules(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Owner/admin can update; publishing works; published to draft returns 409."""
    inst = create_test_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    create_test_user(real_db_session, "other@test.edu", UserRole.INSTRUCTOR)
    create_test_user(real_db_session, "admin@test.edu", UserRole.ADMIN)

    course = Course(
        instructor_id=inst.id,
        title="Original Title",
        description="Original Desc",
        status=CourseStatus.DRAFT,
    )
    real_db_session.add(course)
    real_db_session.commit()

    # Other instructor cannot edit -> 403
    login_test_user(real_db_client, "other@test.edu")
    resp_other = real_db_client.patch(
        f"/api/courses/{course.id}",
        json={"title": "Hacked Title"},
    )
    assert resp_other.status_code == 403

    # Owner publishes course
    login_test_user(real_db_client, "inst@test.edu")
    resp_pub = real_db_client.patch(
        f"/api/courses/{course.id}",
        json={"title": "Updated Title", "status": "published"},
    )
    assert resp_pub.status_code == 200
    assert resp_pub.json()["status"] == "published"
    assert resp_pub.json()["title"] == "Updated Title"

    # Attempt to revert from published to draft -> 409
    resp_conflict = real_db_client.patch(
        f"/api/courses/{course.id}",
        json={"status": "draft"},
    )
    assert resp_conflict.status_code == 409
    assert resp_conflict.json()["code"] == "INVALID_STATUS_TRANSITION"

    # Admin can update title of published course
    login_test_user(real_db_client, "admin@test.edu")
    resp_admin = real_db_client.patch(
        f"/api/courses/{course.id}",
        json={"title": "Admin Modified Title"},
    )
    assert resp_admin.status_code == 200
    assert resp_admin.json()["title"] == "Admin Modified Title"
