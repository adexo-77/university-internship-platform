"""Integration tests for the instructor dashboard endpoint."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import UserRole
from tests.factories import (
    create_test_student,
    create_test_user,
    login_test_user,
)


def test_instructor_dashboard_role_guards(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Only authenticated instructors may access the instructor dashboard."""
    real_db_client.cookies.clear()
    assert real_db_client.get("/api/dashboard/instructor").status_code == 401

    for role in [UserRole.STUDENT, UserRole.ORGANIZATION, UserRole.ADMIN]:
        u = create_test_user(real_db_session, f"inst_guard_{role.value}@test.com", role)
        login_test_user(real_db_client, u.email)
        assert real_db_client.get("/api/dashboard/instructor").status_code == 403

    instructor = create_test_user(real_db_session, "inst_guard_ok@test.com", UserRole.INSTRUCTOR)
    login_test_user(real_db_client, instructor.email)
    assert real_db_client.get("/api/dashboard/instructor").status_code == 200


def test_instructor_dashboard_empty_state(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Empty instructor account returns empty courses list and empty needs_grading list."""
    instructor = create_test_user(real_db_session, "inst_empty@test.com", UserRole.INSTRUCTOR)
    login_test_user(real_db_client, instructor.email)

    resp = real_db_client.get("/api/dashboard/instructor")
    assert resp.status_code == 200
    data = resp.json()
    assert data["courses"] == []
    assert data["needs_grading"] == []


def test_instructor_dashboard_metrics_and_isolation(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Instructor dashboard calculates course metrics, orders needs_grading, and isolates data."""
    inst_a = create_test_user(real_db_session, "inst_metrics_a@test.com", UserRole.INSTRUCTOR)
    inst_b = create_test_user(real_db_session, "inst_metrics_b@test.com", UserRole.INSTRUCTOR)
    student_1, _ = create_test_student(real_db_session, "inst_stud_1@test.com", "Alice Student")
    student_2, _ = create_test_student(real_db_session, "inst_stud_2@test.com", "Bob Student")

    # Instructor A course 1
    c1 = Course(
        instructor_id=inst_a.id,
        title="Distributed Systems",
        status=CourseStatus.PUBLISHED,
    )
    # Instructor A course 2 (empty)
    c2 = Course(
        instructor_id=inst_a.id,
        title="Compiler Design",
        status=CourseStatus.DRAFT,
    )
    # Instructor B course (isolation test)
    c_b = Course(
        instructor_id=inst_b.id,
        title="Other Instructor Course",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add_all([c1, c2, c_b])
    real_db_session.commit()

    # Enrollments
    real_db_session.add_all(
        [
            Enrollment(course_id=c1.id, student_id=student_1.id),
            Enrollment(course_id=c1.id, student_id=student_2.id),
            Enrollment(course_id=c_b.id, student_id=student_1.id),
        ]
    )
    real_db_session.commit()

    now = datetime.now(UTC)
    a1 = Assignment(
        course_id=c1.id,
        title="Lab 1",
        due_at=now + timedelta(days=5),
        max_points=100,
    )
    a2 = Assignment(
        course_id=c1.id,
        title="Lab 2",
        due_at=now + timedelta(days=7),
        max_points=50,
    )
    real_db_session.add_all([a1, a2])
    real_db_session.commit()

    # Submissions:
    # 1. student_1 Lab 1: graded 90/100 (90%)
    sub_graded = Submission(
        assignment_id=a1.id,
        student_id=student_1.id,
        content="Lab 1 solution",
        grade=90,
        graded_at=now,
    )
    # 2. student_2 Lab 1: ungraded, submitted 2 days ago (older)
    sub_older_ungraded = Submission(
        assignment_id=a1.id,
        student_id=student_2.id,
        content="Lab 1 Bob",
        grade=None,
        is_late=False,
    )
    # 3. student_1 Lab 2: ungraded, submitted 1 day ago (newer, late)
    sub_newer_ungraded = Submission(
        assignment_id=a2.id,
        student_id=student_1.id,
        content="Lab 2 Alice",
        grade=None,
        is_late=True,
    )
    real_db_session.add_all([sub_graded, sub_older_ungraded, sub_newer_ungraded])
    real_db_session.commit()

    # Backdate submitted_at to test ordering
    sub_older_ungraded.submitted_at = now - timedelta(days=2)
    sub_newer_ungraded.submitted_at = now - timedelta(days=1)
    real_db_session.commit()

    login_test_user(real_db_client, inst_a.email)
    resp = real_db_client.get("/api/dashboard/instructor")
    assert resp.status_code == 200
    data = resp.json()

    # Course list and metrics
    courses = data["courses"]
    assert len(courses) == 2
    c1_data = next(c for c in courses if c["course_id"] == c1.id)
    assert c1_data["title"] == "Distributed Systems"
    assert c1_data["enrolled_count"] == 2
    assert c1_data["assignments_count"] == 2
    assert c1_data["submissions_awaiting_grading"] == 2
    assert c1_data["average_grade_percent"] == 90.0

    c2_data = next(c for c in courses if c["course_id"] == c2.id)
    assert c2_data["title"] == "Compiler Design"
    assert c2_data["enrolled_count"] == 0
    assert c2_data["assignments_count"] == 0
    assert c2_data["submissions_awaiting_grading"] == 0
    assert c2_data["average_grade_percent"] is None

    # Needs grading list: ordered oldest submitted first
    needs = data["needs_grading"]
    assert len(needs) == 2
    assert needs[0]["submission_id"] == sub_older_ungraded.id
    assert needs[0]["assignment_title"] == "Lab 1"
    assert needs[0]["course_title"] == "Distributed Systems"
    assert needs[0]["late"] is False

    assert needs[1]["submission_id"] == sub_newer_ungraded.id
    assert needs[1]["assignment_title"] == "Lab 2"
    assert needs[1]["late"] is True
