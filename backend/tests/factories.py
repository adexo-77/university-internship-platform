"""Test data factories and authentication helpers for backend test suites."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.application import Application, ApplicationStatus
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.internship import Internship, InternshipStatus, InternshipWorkMode
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


def create_test_internship(
    db: Session,
    organization: User,
    title: str = "Software Engineering Intern",
    status: InternshipStatus = InternshipStatus.OPEN,
    deadline_delta_days: int = 14,
    work_mode: InternshipWorkMode = InternshipWorkMode.HYBRID,
    duration_weeks: int | None = 12,
) -> Internship:
    """Helper to seed an internship posting directly in the database."""
    posting = Internship(
        organization_id=organization.id,
        title=title,
        description="Build state-of-the-art web systems.",
        requirements="Python, React, and SQL proficiency.",
        location="Nairobi, Kenya",
        work_mode=work_mode,
        duration_weeks=duration_weeks,
        application_deadline=datetime.now(UTC) + timedelta(days=deadline_delta_days),
        status=status,
    )
    db.add(posting)
    db.commit()
    db.refresh(posting)
    return posting


def create_test_application(
    db: Session,
    posting: Internship,
    student: User,
    cover_letter: str = "I am deeply interested in this software internship.",
    status: ApplicationStatus = ApplicationStatus.SUBMITTED,
) -> Application:
    """Helper to seed an application directly in the database."""
    app = Application(
        posting_id=posting.id,
        student_id=student.id,
        cover_letter=cover_letter,
        status=status,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app
