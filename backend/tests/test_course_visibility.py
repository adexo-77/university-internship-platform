"""Integration tests for course visibility, catalog search, pagination, and enrollment flags."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_draft_course_visibility_and_admin_access(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Drafts return 404 to non-owners; owners and admin can access."""
    inst1 = create_test_user(real_db_session, "owner@test.edu", UserRole.INSTRUCTOR)
    create_test_user(real_db_session, "other@test.edu", UserRole.INSTRUCTOR)
    create_test_user(real_db_session, "stud@test.edu", UserRole.STUDENT)
    create_test_user(real_db_session, "admin@test.edu", UserRole.ADMIN)

    # Seed draft course
    course = Course(
        instructor_id=inst1.id,
        title="Draft Course",
        description="Private notes",
        status=CourseStatus.DRAFT,
    )
    real_db_session.add(course)
    real_db_session.commit()

    # Other instructor -> 404
    login_test_user(real_db_client, "other@test.edu")
    assert real_db_client.get(f"/api/courses/{course.id}").status_code == 404

    # Student -> 404
    login_test_user(real_db_client, "stud@test.edu")
    assert real_db_client.get(f"/api/courses/{course.id}").status_code == 404

    # Owner -> 200
    login_test_user(real_db_client, "owner@test.edu")
    resp_owner = real_db_client.get(f"/api/courses/{course.id}")
    assert resp_owner.status_code == 200
    assert resp_owner.json()["title"] == "Draft Course"

    # Admin -> 200
    login_test_user(real_db_client, "admin@test.edu")
    resp_admin = real_db_client.get(f"/api/courses/{course.id}")
    assert resp_admin.status_code == 200


def test_course_search_and_pagination(real_db_client: TestClient, real_db_session: Session) -> None:
    """Course listing supports ?q= search, limit, offset, and admin sees drafts."""
    inst = create_test_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    create_test_user(real_db_session, "stud@test.edu", UserRole.STUDENT)
    create_test_user(real_db_session, "admin@test.edu", UserRole.ADMIN)

    for i in range(1, 6):
        real_db_session.add(
            Course(
                instructor_id=inst.id,
                title=f"Python Programming {i}",
                status=CourseStatus.PUBLISHED,
            )
        )
    # Draft course
    real_db_session.add(
        Course(
            instructor_id=inst.id,
            title="Python Advanced Draft",
            status=CourseStatus.DRAFT,
        )
    )
    real_db_session.commit()

    # Student sees only 5 published
    login_test_user(real_db_client, "stud@test.edu")
    resp_student = real_db_client.get("/api/courses?q=Python")
    assert resp_student.status_code == 200
    body = resp_student.json()
    assert body["total"] == 5
    assert len(body["items"]) == 5

    # Pagination
    resp_page = real_db_client.get("/api/courses?limit=2&offset=2")
    assert resp_page.status_code == 200
    page_data = resp_page.json()
    assert len(page_data["items"]) == 2
    assert page_data["total"] == 5

    # Admin sees 6 (including draft)
    login_test_user(real_db_client, "admin@test.edu")
    resp_admin = real_db_client.get("/api/courses?q=Python")
    assert resp_admin.status_code == 200
    assert resp_admin.json()["total"] == 6


def test_enrolled_flag_is_per_student_and_my_courses(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """The enrolled flag in listing is per student and my courses returns enrolled."""
    inst = create_test_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    s1 = create_test_user(real_db_session, "s1@test.edu", UserRole.STUDENT)
    create_test_user(real_db_session, "s2@test.edu", UserRole.STUDENT)

    course = Course(
        instructor_id=inst.id,
        title="Distributed Systems",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.commit()

    # Enroll s1
    real_db_session.add(Enrollment(course_id=course.id, student_id=s1.id))
    real_db_session.commit()

    # s1 sees enrolled == True
    login_test_user(real_db_client, "s1@test.edu")
    r1 = real_db_client.get("/api/courses").json()
    assert r1["items"][0]["enrolled"] is True

    # s1 my-courses returns 1 course
    s1_courses = real_db_client.get("/api/students/me/courses").json()
    assert len(s1_courses) == 1
    assert s1_courses[0]["id"] == course.id

    # s2 sees enrolled == False
    login_test_user(real_db_client, "s2@test.edu")
    r2 = real_db_client.get("/api/courses").json()
    assert r2["items"][0]["enrolled"] is False

    # s2 my-courses returns 0 courses
    s2_courses = real_db_client.get("/api/students/me/courses").json()
    assert len(s2_courses) == 0

    # Instructor my-courses includes enrolled_count == 1
    login_test_user(real_db_client, "inst@test.edu")
    inst_courses = real_db_client.get("/api/instructors/me/courses").json()
    assert len(inst_courses) == 1
    assert inst_courses[0]["enrolled_count"] == 1
