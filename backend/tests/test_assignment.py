"""Integration tests for assignment creation, visibility, updates, and deletion."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import User, UserRole


def _create_user(
    db: Session,
    email: str,
    role: UserRole,
    password: str = "Password123!",
    full_name: str = "Test User",
) -> User:
    """Helper to seed a user directly in the database."""
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _login(client: TestClient, email: str, password: str = "Password123!") -> None:
    """Helper to authenticate a test client via login endpoint."""
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200


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
    inst1 = _create_user(real_db_session, "inst1@test.edu", UserRole.INSTRUCTOR)
    inst2 = _create_user(real_db_session, "inst2@test.edu", UserRole.INSTRUCTOR)
    stud = _create_user(real_db_session, "stud@test.edu", UserRole.STUDENT)
    course = _seed_course(real_db_session, inst1)

    future_due = (datetime.now(UTC) + timedelta(days=7)).isoformat()
    past_due = (datetime.now(UTC) - timedelta(days=1)).isoformat()

    # Student -> 403
    _login(real_db_client, stud.email)
    res = real_db_client.post(
        f"/api/courses/{course.id}/assignments",
        json={"title": "Assignment 1", "due_at": future_due, "max_points": 100},
    )
    assert res.status_code == 403

    # Other instructor -> 403
    _login(real_db_client, inst2.email)
    res = real_db_client.post(
        f"/api/courses/{course.id}/assignments",
        json={"title": "Assignment 1", "due_at": future_due, "max_points": 100},
    )
    assert res.status_code == 403

    # Owner instructor with past due date -> 422
    _login(real_db_client, inst1.email)
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
    inst = _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    other_inst = _create_user(real_db_session, "other_inst@test.edu", UserRole.INSTRUCTOR)
    admin = _create_user(real_db_session, "admin@test.edu", UserRole.ADMIN)
    enrolled_stud = _create_user(real_db_session, "enrolled@test.edu", UserRole.STUDENT)
    other_stud = _create_user(real_db_session, "other@test.edu", UserRole.STUDENT)

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
    _login(real_db_client, other_stud.email)
    res = real_db_client.get(f"/api/courses/{course.id}/assignments")
    assert res.status_code == 404
    res = real_db_client.get(f"/api/assignments/{assignment.id}")
    assert res.status_code == 404

    # Other instructor -> 404
    _login(real_db_client, other_inst.email)
    res = real_db_client.get(f"/api/courses/{course.id}/assignments")
    assert res.status_code == 404
    res = real_db_client.get(f"/api/assignments/{assignment.id}")
    assert res.status_code == 404

    # Enrolled student -> 200 with submission_status
    _login(real_db_client, enrolled_stud.email)
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
    _login(real_db_client, admin.email)
    res = real_db_client.get(f"/api/courses/{course.id}/assignments")
    assert res.status_code == 200
    assert len(res.json()) == 1

    # Owner instructor -> 200
    _login(real_db_client, inst.email)
    res = real_db_client.get(f"/api/courses/{course.id}/assignments")
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_assignment_patch_max_points_conflict_with_existing_grade(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """max_points cannot be dropped below an existing grade."""
    inst = _create_user(real_db_session, "inst_patch@test.edu", UserRole.INSTRUCTOR)
    stud = _create_user(real_db_session, "stud_patch@test.edu", UserRole.STUDENT)
    course = _seed_course(real_db_session, inst)
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud.id))
    assignment = Assignment(
        course_id=course.id,
        title="Project",
        due_at=datetime.now(UTC) + timedelta(days=5),
        max_points=100,
    )
    real_db_session.add(assignment)
    real_db_session.commit()
    real_db_session.refresh(assignment)

    # Seed an existing graded submission with 85
    sub = Submission(
        assignment_id=assignment.id,
        student_id=stud.id,
        content="Final project submission",
        grade=85,
        graded_at=datetime.now(UTC),
        graded_by=inst.id,
    )
    real_db_session.add(sub)
    real_db_session.commit()

    _login(real_db_client, inst.email)

    # Attempt to lower max_points to 80 -> 409
    res = real_db_client.patch(
        f"/api/assignments/{assignment.id}",
        json={"max_points": 80},
    )
    assert res.status_code == 409

    # Lowering max_points to 90 is valid
    res = real_db_client.patch(
        f"/api/assignments/{assignment.id}",
        json={"max_points": 90, "title": "Updated Project Title"},
    )
    assert res.status_code == 200
    assert res.json()["max_points"] == 90
    assert res.json()["title"] == "Updated Project Title"


def test_assignment_delete_blocked_when_submissions_exist(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Deleting an assignment is forbidden with 409 if submissions exist."""
    inst = _create_user(real_db_session, "inst_del@test.edu", UserRole.INSTRUCTOR)
    stud = _create_user(real_db_session, "stud_del@test.edu", UserRole.STUDENT)
    course = _seed_course(real_db_session, inst)
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud.id))
    assignment = Assignment(
        course_id=course.id,
        title="Lab 1",
        due_at=datetime.now(UTC) + timedelta(days=5),
        max_points=50,
    )
    real_db_session.add(assignment)
    real_db_session.commit()
    real_db_session.refresh(assignment)

    sub = Submission(
        assignment_id=assignment.id,
        student_id=stud.id,
        content="Lab answers",
    )
    real_db_session.add(sub)
    real_db_session.commit()

    _login(real_db_client, inst.email)

    # Deleting assignment with submission -> 409
    res = real_db_client.delete(f"/api/assignments/{assignment.id}")
    assert res.status_code == 409

    # Remove submission, then delete succeeds -> 204
    real_db_session.delete(sub)
    real_db_session.commit()

    res = real_db_client.delete(f"/api/assignments/{assignment.id}")
    assert res.status_code == 204

    # Subsequent get -> 404
    res = real_db_client.get(f"/api/assignments/{assignment.id}")
    assert res.status_code == 404
