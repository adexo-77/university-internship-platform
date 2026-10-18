"""Integration tests for assignment creation and visibility rules."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from tests.factories import create_test_user, login_test_user


def _seed_course(
    db: Session, instructor: User, status: CourseStatus = CourseStatus.PUBLISHED
) -> Course:
    course = Course(
        instructor_id=instructor.id,
        title="Web Systems Architecture",
        description="Core computing",
        status=status,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def test_assignment_creation_instructor_only_and_future_due(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Instructors can create assignments for their courses; non-owners and students get 403."""
    inst1 = create_test_user(real_db_session, "inst1@test.edu", UserRole.INSTRUCTOR)
    inst2 = create_test_user(real_db_session, "inst2@test.edu", UserRole.INSTRUCTOR)
    stud = create_test_user(real_db_session, "stud@test.edu", UserRole.STUDENT)
    course = _seed_course(real_db_session, inst1)

    future_due = (datetime.now(UTC) + timedelta(days=7)).isoformat()
    past_due = (datetime.now(UTC) - timedelta(days=1)).isoformat()

    # Student -> 403
    login_test_user(real_db_client, stud.email)
    res = real_db_client.post(
        f"/api/courses/{course.id}/assignments",
        json={"title": "Assignment 1", "due_at": future_due, "max_points": 100},
    )
    assert res.status_code == 403

    # Other instructor -> 403
    login_test_user(real_db_client, inst2.email)
    res = real_db_client.post(
        f"/api/courses/{course.id}/assignments",
        json={"title": "Assignment 1", "due_at": future_due, "max_points": 100},
    )
    assert res.status_code == 403

    # Owner instructor with past due date -> 422
    login_test_user(real_db_client, inst1.email)
    res = real_db_client.post(
        f"/api/courses/{course.id}/assignments",
        json={"title": "Assignment 1", "due_at": past_due, "max_points": 100},
    )
    assert res.status_code in (409, 422)

    # Owner instructor with extra forbidden field -> 422
    res = real_db_client.post(
        f"/api/courses/{course.id}/assignments",
        json={
            "title": "Assignment 1",
            "due_at": future_due,
            "max_points": 100,
            "student_id": 99,
        },
    )
    assert res.status_code == 422

    # Owner instructor success
    res = real_db_client.post(
        f"/api/courses/{course.id}/assignments",
        json={"title": "Assignment 1", "description": "Solve problems", "due_at": future_due},
    )
    assert res.status_code == 201
    data = res.json()
    assert data["title"] == "Assignment 1"
    assert data["max_points"] == 100
    assert data["course_id"] == course.id
    assert data["course_title"] == "Web Systems Architecture"


def test_assignment_visibility_rules(real_db_client: TestClient, real_db_session: Session) -> None:
    """Owner, admin, and enrolled student see assignments; others get 404."""
    inst = create_test_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    other_inst = create_test_user(real_db_session, "other_inst@test.edu", UserRole.INSTRUCTOR)
    admin = create_test_user(real_db_session, "admin@test.edu", UserRole.ADMIN)
    enrolled_stud = create_test_user(real_db_session, "enrolled@test.edu", UserRole.STUDENT)
    other_stud = create_test_user(real_db_session, "other@test.edu", UserRole.STUDENT)

    course = _seed_course(real_db_session, inst)
    real_db_session.add(Enrollment(course_id=course.id, student_id=enrolled_stud.id))
    due = datetime.now(UTC) + timedelta(days=5)
    assignment = Assignment(
        course_id=course.id,
        title="Homework 1",
        description="Intro tasks",
        due_at=due,
        max_points=50,
    )
    real_db_session.add(assignment)
    real_db_session.commit()
    real_db_session.refresh(assignment)

    # Non-enrolled student -> 404
    login_test_user(real_db_client, other_stud.email)
    res = real_db_client.get(f"/api/courses/{course.id}/assignments")
    assert res.status_code == 404
    res = real_db_client.get(f"/api/assignments/{assignment.id}")
    assert res.status_code == 404

    # Other instructor -> 404
    login_test_user(real_db_client, other_inst.email)
    res = real_db_client.get(f"/api/courses/{course.id}/assignments")
    assert res.status_code == 404
    res = real_db_client.get(f"/api/assignments/{assignment.id}")
    assert res.status_code == 404

    # Enrolled student -> 200 with submission_status
    login_test_user(real_db_client, enrolled_stud.email)
    res = real_db_client.get(f"/api/courses/{course.id}/assignments")
    assert res.status_code == 200
    items = res.json()
    assert len(items) == 1
    assert items[0]["submission_status"] == "not_submitted"
    assert items[0]["course_title"] == "Web Systems Architecture"

    res = real_db_client.get(f"/api/assignments/{assignment.id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["submission_status"] == "not_submitted"
    assert detail["course_title"] == "Web Systems Architecture"

    # Admin -> 200
    login_test_user(real_db_client, admin.email)
    res = real_db_client.get(f"/api/courses/{course.id}/assignments")
    assert res.status_code == 200
    assert len(res.json()) == 1

    # Owner instructor -> 200
    login_test_user(real_db_client, inst.email)
    res = real_db_client.get(f"/api/courses/{course.id}/assignments")
    assert res.status_code == 200
    assert len(res.json()) == 1
