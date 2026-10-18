"""Test data factories and authentication helpers for backend test suites."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.user import User, UserRole


def create_test_user(
    db: Session,
    email: str,
    role: UserRole,
    password: str = "Password123!",
    full_name: str = "Test User",
) -> User:
    """Helper to seed a user directly in the test database."""
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


def login_test_user(client: TestClient, email: str, password: str = "Password123!") -> None:
    """Helper to authenticate a test client via login endpoint."""
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200


def seed_course_and_assignment(
    db: Session,
    instructor: User,
    due_delta_days: int = 5,
    max_points: int = 100,
) -> tuple[Course, Assignment]:
    """Helper to seed a published course and assignment."""
    course = Course(
        instructor_id=instructor.id,
        title="Algorithms",
        description="Data structures & algos",
        status=CourseStatus.PUBLISHED,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    assignment = Assignment(
        course_id=course.id,
        title="Problem Set 1",
        description="Graph theory",
        due_at=datetime.now(UTC) + timedelta(days=due_delta_days),
        max_points=max_points,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return course, assignment
