"""Tests for the Course and Assignment detail access matrix across roles.

Policy:
- Course & assignment details: enrolled students, owning instructor, admin.
  (Published courses stay visible to students for enrolling).
- Course resources: enrolled students, owning instructor, admin.
- Organizations and coordinators have no access to course internals or assignments.
Asserts status codes (200, 401, 403, 404) and no data leaks on refusal.
"""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.course_resource import CourseResource
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def _seed_course_data(db: Session) -> dict:
    now = datetime.now(UTC)
    inst_owner = create_test_user(db, "inst_owner@matrix.edu", UserRole.INSTRUCTOR)
    inst_other = create_test_user(db, "inst_other@matrix.edu", UserRole.INSTRUCTOR)
    stud_enrolled = create_test_user(db, "stud_enrolled@matrix.edu", UserRole.STUDENT)
    stud_other = create_test_user(db, "stud_other@matrix.edu", UserRole.STUDENT)
    org_owner = create_test_user(db, "org_owner@matrix.edu", UserRole.ORGANIZATION)
    coord = create_test_user(db, "coord@matrix.edu", UserRole.COORDINATOR)
    admin = create_test_user(db, "admin@matrix.edu", UserRole.ADMIN)

    course_pub = Course(
        instructor_id=inst_owner.id,
        title="Published Database Systems",
        description="SQL and normalization",
        status=CourseStatus.PUBLISHED,
    )
    course_draft = Course(
        instructor_id=inst_owner.id,
        title="Draft Advanced Algorithms",
        description="Graph theory notes",
        status=CourseStatus.DRAFT,
    )
    db.add_all([course_pub, course_draft])
    db.flush()

    db.add(Enrollment(course_id=course_pub.id, student_id=stud_enrolled.id))
    db.add(
        CourseResource(
            course_id=course_pub.id,
            title="Database Lecture Slides",
            url="https://example.com/slides.pdf",
        )
    )
    assignment = Assignment(
        course_id=course_pub.id,
        title="SQL Homework 1",
        description="Write complex joins",
        due_at=now + timedelta(days=7),
        max_points=100,
    )
    db.add(assignment)
    db.flush()

    db.add(
        Submission(
            assignment_id=assignment.id,
            student_id=stud_enrolled.id,
            content="SELECT * FROM students;",
            submitted_at=now,
        )
    )
    db.commit()

    return {
        "inst_owner": inst_owner,
        "inst_other": inst_other,
        "stud_enrolled": stud_enrolled,
        "stud_other": stud_other,
        "org_owner": org_owner,
        "coord": coord,
        "admin": admin,
        "course_pub": course_pub,
        "course_draft": course_draft,
        "assignment": assignment,
    }


def _check_leak(resp, terms: list[str]) -> None:
    if resp.status_code in (401, 403, 404):
        body = resp.text.lower()
        for term in terms:
            assert term.lower() not in body, f"Leaked '{term}' in {resp.status_code}"


def test_course_and_resource_access_matrix(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Course and resource detail endpoints enforce access rules and do not leak data."""
    data = _seed_course_data(real_db_session)
    cid = data["course_pub"].id
    terms = ["SQL and normalization", "Database Lecture Slides"]

    course_matrix = {
        None: 401,
        "stud_enrolled": 200,
        "stud_other": 200,
        "inst_owner": 200,
        "inst_other": 404,
        "org_owner": 404,
        "coord": 404,
        "admin": 200,
    }
    resource_matrix = {
        None: 401,
        "stud_enrolled": 200,
        "stud_other": 404,
        "inst_owner": 200,
        "inst_other": 404,
        "org_owner": 404,
        "coord": 404,
        "admin": 200,
    }

    for user_key, expected in course_matrix.items():
        if user_key:
            login_test_user(real_db_client, data[user_key].email)
        else:
            real_db_client.cookies.clear()
        r = real_db_client.get(f"/api/courses/{cid}")
        assert r.status_code == expected, f"Course detail mismatch for {user_key}"
        _check_leak(r, terms)

    for user_key, expected in resource_matrix.items():
        if user_key:
            login_test_user(real_db_client, data[user_key].email)
        else:
            real_db_client.cookies.clear()
        r = real_db_client.get(f"/api/courses/{cid}/resources")
        assert r.status_code == expected, f"Resources mismatch for {user_key}"
        _check_leak(r, terms)


def test_assignment_detail_and_roster_access_matrix(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Assignment detail and roster endpoints enforce strict isolation."""
    data = _seed_course_data(real_db_session)
    aid = data["assignment"].id
    terms = ["Write complex joins", "SELECT * FROM students;"]

    assignment_matrix = {
        None: 401,
        "stud_enrolled": 200,
        "stud_other": 404,
        "inst_owner": 200,
        "inst_other": 404,
        "org_owner": 404,
        "coord": 404,
        "admin": 200,
    }
    roster_matrix = {
        None: 401,
        "stud_enrolled": 403,
        "stud_other": 403,
        "inst_owner": 200,
        "inst_other": 404,
        "org_owner": 403,
        "coord": 403,
        "admin": 200,
    }

    for user_key, expected in assignment_matrix.items():
        if user_key:
            login_test_user(real_db_client, data[user_key].email)
        else:
            real_db_client.cookies.clear()
        r = real_db_client.get(f"/api/assignments/{aid}")
        assert r.status_code == expected, f"Assignment mismatch for {user_key}"
        _check_leak(r, terms)

    for user_key, expected in roster_matrix.items():
        if user_key:
            login_test_user(real_db_client, data[user_key].email)
        else:
            real_db_client.cookies.clear()
        r = real_db_client.get(f"/api/assignments/{aid}/submissions")
        assert r.status_code == expected, f"Roster mismatch for {user_key}"
        _check_leak(r, terms)
