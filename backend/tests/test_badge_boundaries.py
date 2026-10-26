"""Tests for student achievement badge boundaries (submissions, grades, course, profile)."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.student_profile import StudentProfile
from app.models.submission import Submission
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_badge_first_submission_and_ontime_habit_boundary(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify first_submission (0 vs 1) and ontime_habit (4 vs 5, late ignored) boundaries."""
    student = create_test_user(real_db_session, "badge_sub@example.com", UserRole.STUDENT)
    instructor = create_test_user(real_db_session, "badge_inst1@example.com", UserRole.INSTRUCTOR)
    course = Course(instructor_id=instructor.id, title="Physics", status=CourseStatus.PUBLISHED)
    real_db_session.add(course)
    real_db_session.commit()

    login_test_user(real_db_client, student.email)
    resp = real_db_client.get("/api/students/me/badges")
    assert resp.status_code == 200
    badges = {b["id"]: b for b in resp.json()}
    assert badges["first_submission"]["earned"] is False
    assert badges["first_submission"]["progress"] == {"current": 0, "target": 1}
    assert badges["ontime_habit"]["earned"] is False
    assert badges["ontime_habit"]["progress"] == {"current": 0, "target": 5}

    due = datetime.now(UTC) + timedelta(days=2)
    for i in range(4):
        a = Assignment(course_id=course.id, title=f"A{i}", due_at=due, max_points=100)
        real_db_session.add(a)
        real_db_session.flush()
        s = Submission(assignment_id=a.id, student_id=student.id, content="work", is_late=False)
        real_db_session.add(s)

    late_a = Assignment(course_id=course.id, title="LateA", due_at=due, max_points=100)
    real_db_session.add(late_a)
    real_db_session.flush()
    real_db_session.add(
        Submission(assignment_id=late_a.id, student_id=student.id, content="late", is_late=True)
    )
    real_db_session.commit()

    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["first_submission"]["earned"] is True
    assert badges["first_submission"]["progress"] == {"current": 1, "target": 1}
    # 4 on-time + 1 late = 4 on-time (unearned at boundary 4 of 5)
    assert badges["ontime_habit"]["earned"] is False
    assert badges["ontime_habit"]["progress"] == {"current": 4, "target": 5}

    # 5th on-time submission triggers ontime_habit
    a5 = Assignment(course_id=course.id, title="A5", due_at=due, max_points=100)
    real_db_session.add(a5)
    real_db_session.flush()
    real_db_session.add(
        Submission(assignment_id=a5.id, student_id=student.id, content="work5", is_late=False)
    )
    real_db_session.commit()

    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["ontime_habit"]["earned"] is True
    assert badges["ontime_habit"]["progress"] == {"current": 5, "target": 5}


def test_badge_high_achiever_and_perfect_score_boundary(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify 89.9% vs 90% boundary and max_points - 1 vs max_points boundary."""
    student = create_test_user(real_db_session, "badge_grades@example.com", UserRole.STUDENT)
    instructor = create_test_user(real_db_session, "badge_inst2@example.com", UserRole.INSTRUCTOR)
    course = Course(instructor_id=instructor.id, title="Math", status=CourseStatus.PUBLISHED)
    real_db_session.add(course)
    real_db_session.commit()

    # 899/1000 = 89.9% -> high achiever not earned, perfect score not earned
    a1 = Assignment(
        course_id=course.id,
        title="Hard Exam",
        due_at=datetime.now(UTC) + timedelta(days=1),
        max_points=1000,
    )
    real_db_session.add(a1)
    real_db_session.flush()
    real_db_session.add(
        Submission(assignment_id=a1.id, student_id=student.id, content="ans", grade=899)
    )
    real_db_session.commit()

    login_test_user(real_db_client, student.email)
    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["high_achiever"]["earned"] is False
    assert badges["high_achiever"]["progress"] is None
    assert badges["perfect_score"]["earned"] is False
    assert badges["perfect_score"]["progress"] is None

    # Score exactly 90/100 (90.0%) -> high achiever earned
    a2 = Assignment(
        course_id=course.id,
        title="Quiz",
        due_at=datetime.now(UTC) + timedelta(days=1),
        max_points=100,
    )
    real_db_session.add(a2)
    real_db_session.flush()
    real_db_session.add(
        Submission(assignment_id=a2.id, student_id=student.id, content="ans", grade=90)
    )
    real_db_session.commit()

    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["high_achiever"]["earned"] is True
    assert badges["perfect_score"]["earned"] is False

    # Score 50/50 -> perfect score earned
    a3 = Assignment(
        course_id=course.id,
        title="Lab",
        due_at=datetime.now(UTC) + timedelta(days=1),
        max_points=50,
    )
    real_db_session.add(a3)
    real_db_session.flush()
    real_db_session.add(
        Submission(assignment_id=a3.id, student_id=student.id, content="ans", grade=50)
    )
    real_db_session.commit()

    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["perfect_score"]["earned"] is True


def test_badge_course_finisher_and_profile_complete_boundary(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify course finisher (0 vs 1 vs 2 of 2) and profile complete (4 vs 5 fields)."""
    student = create_test_user(real_db_session, "badge_finish@example.com", UserRole.STUDENT)
    instructor = create_test_user(real_db_session, "badge_inst3@example.com", UserRole.INSTRUCTOR)
    c_empty = Course(instructor_id=instructor.id, title="Empty", status=CourseStatus.PUBLISHED)
    c_two = Course(instructor_id=instructor.id, title="TwoA", status=CourseStatus.PUBLISHED)
    real_db_session.add_all([c_empty, c_two])
    real_db_session.commit()

    real_db_session.add(Enrollment(course_id=c_empty.id, student_id=student.id))
    real_db_session.add(Enrollment(course_id=c_two.id, student_id=student.id))

    a1 = Assignment(
        course_id=c_two.id,
        title="Part 1",
        due_at=datetime.now(UTC) + timedelta(days=1),
        max_points=100,
    )
    a2 = Assignment(
        course_id=c_two.id,
        title="Part 2",
        due_at=datetime.now(UTC) + timedelta(days=1),
        max_points=100,
    )
    real_db_session.add_all([a1, a2])

    # 4 profile fields filled (missing skills)
    prof = StudentProfile(
        user_id=student.id,
        university="Addis Ababa University",
        department="Computer Science",
        year_of_study=4,
        bio="Aspiring engineer",
        skills=[],
    )
    real_db_session.add(prof)
    real_db_session.commit()

    login_test_user(real_db_client, student.email)
    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["course_finisher"]["earned"] is False
    assert badges["course_finisher"]["progress"] == {"current": 0, "target": 2}
    assert badges["profile_complete"]["earned"] is False
    assert badges["profile_complete"]["progress"] == {"current": 4, "target": 5}

    # Submit 1 of 2 assignments & complete 5th profile field
    real_db_session.add(Submission(assignment_id=a1.id, student_id=student.id, content="sub1"))
    prof.skills = ["Python", "PostgreSQL"]
    real_db_session.commit()

    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["course_finisher"]["earned"] is False
    assert badges["course_finisher"]["progress"] == {"current": 1, "target": 2}
    assert badges["profile_complete"]["earned"] is True
    assert badges["profile_complete"]["progress"] == {"current": 5, "target": 5}

    # Submit 2 of 2 assignments -> course finisher earned
    real_db_session.add(Submission(assignment_id=a2.id, student_id=student.id, content="sub2"))
    real_db_session.commit()

    resp = real_db_client.get("/api/students/me/badges")
    badges = {b["id"]: b for b in resp.json()}
    assert badges["course_finisher"]["earned"] is True
    assert badges["course_finisher"]["progress"] == {"current": 2, "target": 2}
