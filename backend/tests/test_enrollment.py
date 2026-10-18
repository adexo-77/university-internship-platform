"""Integration tests for course enrollment, unenrollment, rosters, and cascade deletes."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole


def _create_user(
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


def _login(client: TestClient, email: str, password: str = "Password123!") -> None:
    """Helper to authenticate a test client via login endpoint."""
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200


def test_enrollment_happy_path_and_double_enroll_conflict(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Student can enroll in published course; enrolling twice returns 409."""
    inst = _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    stud = _create_user(real_db_session, "stud@test.edu", UserRole.STUDENT)

    course = Course(
        instructor_id=inst.id,
        title="Web Architecture",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.commit()

    _login(real_db_client, "stud@test.edu")

    # First enrollment -> 201
    resp1 = real_db_client.post(f"/api/courses/{course.id}/enrollment")
    assert resp1.status_code == 201
    assert resp1.json()["student_id"] == stud.id

    # Second enrollment -> 409
    resp2 = real_db_client.post(f"/api/courses/{course.id}/enrollment")
    assert resp2.status_code == 409
    assert resp2.json()["code"] == "ALREADY_ENROLLED"


def test_enrollment_role_restrictions_and_draft_rejection(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Instructors/orgs cannot enroll; draft courses return 404."""
    inst = _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    _create_user(real_db_session, "other_inst@test.edu", UserRole.INSTRUCTOR)
    _create_user(real_db_session, "org@test.edu", UserRole.ORGANIZATION)
    _create_user(real_db_session, "stud@test.edu", UserRole.STUDENT)

    pub_course = Course(
        instructor_id=inst.id,
        title="Published Course",
        status=CourseStatus.PUBLISHED,
    )
    draft_course = Course(
        instructor_id=inst.id,
        title="Draft Course",
        status=CourseStatus.DRAFT,
    )
    real_db_session.add_all([pub_course, draft_course])
    real_db_session.commit()

    # Instructor gets 403
    _login(real_db_client, "other_inst@test.edu")
    assert real_db_client.post(f"/api/courses/{pub_course.id}/enrollment").status_code == 403

    # Org gets 403
    _login(real_db_client, "org@test.edu")
    assert real_db_client.post(f"/api/courses/{pub_course.id}/enrollment").status_code == 403

    # Student enrolling in draft gets 404
    _login(real_db_client, "stud@test.edu")
    assert real_db_client.post(f"/api/courses/{draft_course.id}/enrollment").status_code == 404


def test_leave_course_success_and_not_enrolled_404(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Leaving an enrolled course succeeds; leaving a course not enrolled returns 404."""
    inst = _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    stud = _create_user(real_db_session, "stud@test.edu", UserRole.STUDENT)

    course = Course(
        instructor_id=inst.id,
        title="Computer Networks",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.commit()

    _login(real_db_client, "stud@test.edu")

    # Leaving before enrolling -> 404
    resp_not_in = real_db_client.delete(f"/api/courses/{course.id}/enrollment")
    assert resp_not_in.status_code == 404
    assert resp_not_in.json()["code"] == "NOT_ENROLLED"

    # Enroll
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud.id))
    real_db_session.commit()

    # Leave -> 200
    resp_leave = real_db_client.delete(f"/api/courses/{course.id}/enrollment")
    assert resp_leave.status_code == 200

    # Leave again -> 404
    resp_leave_again = real_db_client.delete(f"/api/courses/{course.id}/enrollment")
    assert resp_leave_again.status_code == 404


def test_course_roster_permissions_and_content(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Owner and admin can view roster; other instructors and students receive 403."""
    inst_owner = _create_user(
        real_db_session, "owner@test.edu", UserRole.INSTRUCTOR, full_name="Prof A"
    )
    _create_user(real_db_session, "other@test.edu", UserRole.INSTRUCTOR, full_name="Prof B")
    _create_user(real_db_session, "admin@test.edu", UserRole.ADMIN, full_name="Admin")
    stud = _create_user(
        real_db_session,
        "alice@student.edu",
        UserRole.STUDENT,
        full_name="Alice Student",
    )

    course = Course(
        instructor_id=inst_owner.id,
        title="Operating Systems",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.commit()

    real_db_session.add(Enrollment(course_id=course.id, student_id=stud.id))
    real_db_session.commit()

    # Student -> 403
    _login(real_db_client, "alice@student.edu")
    assert real_db_client.get(f"/api/courses/{course.id}/students").status_code == 403

    # Other instructor -> 403
    _login(real_db_client, "other@test.edu")
    assert real_db_client.get(f"/api/courses/{course.id}/students").status_code == 403

    # Owner -> 200 with Alice's name and email
    _login(real_db_client, "owner@test.edu")
    resp_owner = real_db_client.get(f"/api/courses/{course.id}/students")
    assert resp_owner.status_code == 200
    roster = resp_owner.json()
    assert len(roster) == 1
    assert roster[0]["student_id"] == stud.id
    assert roster[0]["name"] == "Alice Student"
    assert roster[0]["email"] == "alice@student.edu"

    # Admin -> 200
    _login(real_db_client, "admin@test.edu")
    resp_admin = real_db_client.get(f"/api/courses/{course.id}/students")
    assert resp_admin.status_code == 200
    assert len(resp_admin.json()) == 1


def test_user_deletion_cascades_to_enrollments(real_db_session: Session) -> None:
    """Deleting a user removes their enrollments automatically via foreign key CASCADE."""
    inst = _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    stud = _create_user(real_db_session, "stud@test.edu", UserRole.STUDENT)

    course = Course(
        instructor_id=inst.id,
        title="Algorithms",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.commit()

    real_db_session.add(Enrollment(course_id=course.id, student_id=stud.id))
    real_db_session.commit()

    # Verify enrollment exists
    enrollment = real_db_session.scalar(
        select(Enrollment).where(
            Enrollment.course_id == course.id, Enrollment.student_id == stud.id
        )
    )
    assert enrollment is not None

    # Delete the student user
    real_db_session.delete(stud)
    real_db_session.commit()

    # Verify enrollment is cascaded and removed
    enrollment_after = real_db_session.scalar(
        select(Enrollment).where(Enrollment.course_id == course.id)
    )
    assert enrollment_after is None
