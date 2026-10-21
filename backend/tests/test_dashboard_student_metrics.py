"""Integration tests for student dashboard metrics, ordering, and isolation."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import ApplicationStatus
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.internship import InternshipStatus
from app.models.submission import Submission
from app.models.user import UserRole
from tests.factories import (
    create_test_application,
    create_test_internship,
    create_test_organization,
    create_test_student,
    create_test_user,
    login_test_user,
)


def test_student_dashboard_due_next_filters_and_ordering(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """due_next excludes submitted, past-due, and draft courses, and orders by due_at asc."""
    student, _ = create_test_student(real_db_session, "due_student@test.com")
    instructor = create_test_user(real_db_session, "due_inst@test.com", UserRole.INSTRUCTOR)

    pub_course = Course(
        instructor_id=instructor.id,
        title="Published Course",
        status=CourseStatus.PUBLISHED,
    )
    draft_course = Course(
        instructor_id=instructor.id,
        title="Draft Course",
        status=CourseStatus.DRAFT,
    )
    real_db_session.add_all([pub_course, draft_course])
    real_db_session.commit()

    real_db_session.add_all(
        [
            Enrollment(course_id=pub_course.id, student_id=student.id),
            Enrollment(course_id=draft_course.id, student_id=student.id),
        ]
    )
    real_db_session.commit()

    now = datetime.now(UTC)
    a_soon = Assignment(
        course_id=pub_course.id,
        title="Assignment Soon",
        due_at=now + timedelta(days=2),
        max_points=100,
    )
    a_later = Assignment(
        course_id=pub_course.id,
        title="Assignment Later",
        due_at=now + timedelta(days=5),
        max_points=100,
    )
    a_submitted = Assignment(
        course_id=pub_course.id,
        title="Assignment Submitted",
        due_at=now + timedelta(days=3),
        max_points=100,
    )
    a_past = Assignment(
        course_id=pub_course.id,
        title="Assignment Past",
        due_at=now - timedelta(days=1),
        max_points=100,
    )
    a_draft = Assignment(
        course_id=draft_course.id,
        title="Assignment in Draft Course",
        due_at=now + timedelta(days=4),
        max_points=100,
    )
    real_db_session.add_all([a_soon, a_later, a_submitted, a_past, a_draft])
    real_db_session.commit()

    sub = Submission(
        assignment_id=a_submitted.id,
        student_id=student.id,
        content="Submitted work",
    )
    real_db_session.add(sub)
    real_db_session.commit()

    login_test_user(real_db_client, student.email)
    resp = real_db_client.get("/api/dashboard/student")
    assert resp.status_code == 200
    due_items = resp.json()["due_next"]

    assert len(due_items) == 2
    assert due_items[0]["assignment_id"] == a_soon.id
    assert due_items[0]["title"] == "Assignment Soon"
    assert due_items[0]["course_title"] == "Published Course"
    assert due_items[1]["assignment_id"] == a_later.id


def test_student_dashboard_course_progress_grades_and_isolation(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Tests course progress percent, average grade calculation, and cross-student isolation."""
    student_a, _ = create_test_student(real_db_session, "stud_a@test.com")
    student_b, _ = create_test_student(real_db_session, "stud_b@test.com")
    instructor = create_test_user(real_db_session, "inst_prog@test.com", UserRole.INSTRUCTOR)
    org, _ = create_test_organization(real_db_session, "org_prog@test.com")

    course_1 = Course(
        instructor_id=instructor.id,
        title="Course 1",
        status=CourseStatus.PUBLISHED,
    )
    course_empty = Course(
        instructor_id=instructor.id,
        title="Course Empty",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add_all([course_1, course_empty])
    real_db_session.commit()

    real_db_session.add_all(
        [
            Enrollment(course_id=course_1.id, student_id=student_a.id),
            Enrollment(course_id=course_empty.id, student_id=student_a.id),
            Enrollment(course_id=course_1.id, student_id=student_b.id),
        ]
    )
    real_db_session.commit()

    now = datetime.now(UTC)
    a1 = Assignment(
        course_id=course_1.id,
        title="HW 1",
        due_at=now + timedelta(days=3),
        max_points=100,
    )
    a2 = Assignment(
        course_id=course_1.id,
        title="HW 2",
        due_at=now + timedelta(days=4),
        max_points=50,
    )
    real_db_session.add_all([a1, a2])
    real_db_session.commit()

    now_ts = datetime.now(UTC)
    sub1 = Submission(
        assignment_id=a1.id,
        student_id=student_a.id,
        content="HW1 sol",
        grade=80,
        graded_at=now_ts,
    )
    sub2 = Submission(
        assignment_id=a2.id,
        student_id=student_a.id,
        content="HW2 sol",
        grade=None,
    )
    sub_b = Submission(
        assignment_id=a1.id,
        student_id=student_b.id,
        content="HW1 sol B",
        grade=100,
        graded_at=now_ts,
    )
    real_db_session.add_all([sub1, sub2, sub_b])

    posting = create_test_internship(
        real_db_session,
        org,
        title="Cloud Engineer Intern",
        status=InternshipStatus.OPEN,
    )
    create_test_application(
        real_db_session,
        posting,
        student_a,
        status=ApplicationStatus.SUBMITTED,
    )
    create_test_application(
        real_db_session,
        posting,
        student_b,
        status=ApplicationStatus.SHORTLISTED,
    )
    real_db_session.commit()

    login_test_user(real_db_client, student_a.email)
    resp = real_db_client.get("/api/dashboard/student")
    assert resp.status_code == 200
    data = resp.json()

    c1_data = next(c for c in data["courses"] if c["course_id"] == course_1.id)
    assert c1_data["assignments_total"] == 2
    assert c1_data["assignments_submitted"] == 2
    assert c1_data["progress_percent"] == 100.0
    assert c1_data["average_grade_percent"] == 80.0

    ce_data = next(c for c in data["courses"] if c["course_id"] == course_empty.id)
    assert ce_data["assignments_total"] == 0
    assert ce_data["assignments_submitted"] == 0
    assert ce_data["progress_percent"] == 0.0
    assert ce_data["average_grade_percent"] is None

    assert len(data["recent_grades"]) == 1
    assert data["recent_grades"][0]["grade"] == 80
    assert data["recent_grades"][0]["max_points"] == 100

    assert data["applications"]["counts_by_status"]["submitted"] == 1
    assert data["applications"]["counts_by_status"]["shortlisted"] == 0
    assert len(data["applications"]["recent"]) == 1
    assert data["profile_complete"] is True
