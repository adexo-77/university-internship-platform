"""Integration tests for course endpoints, ownership, visibility, and validation."""

from fastapi.testclient import TestClient
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


def test_course_creation_instructor_only(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Instructors can create courses; students and organizations receive 403."""
    _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    _create_user(real_db_session, "stud@test.edu", UserRole.STUDENT)
    _create_user(real_db_session, "org@test.edu", UserRole.ORGANIZATION)

    # Student -> 403
    _login(real_db_client, "stud@test.edu")
    resp_student = real_db_client.post(
        "/api/courses",
        json={"title": "Data Structures", "description": "CS Course"},
    )
    assert resp_student.status_code == 403

    # Organization -> 403
    _login(real_db_client, "org@test.edu")
    resp_org = real_db_client.post(
        "/api/courses",
        json={"title": "Data Structures", "description": "CS Course"},
    )
    assert resp_org.status_code == 403

    # Instructor -> 201
    _login(real_db_client, "inst@test.edu")
    resp_inst = real_db_client.post(
        "/api/courses",
        json={"title": "Data Structures", "description": "CS Course"},
    )
    assert resp_inst.status_code == 201
    data = resp_inst.json()
    assert data["title"] == "Data Structures"
    assert data["status"] == "draft"
    assert data["instructor_name"] == "Test User"


def test_course_creation_rejects_extra_fields(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """A client can never send instructor_id or unknown fields."""
    _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    _login(real_db_client, "inst@test.edu")

    resp = real_db_client.post(
        "/api/courses",
        json={
            "title": "Machine Learning",
            "instructor_id": 999,
        },
    )
    assert resp.status_code == 422


def test_course_validation_rules(real_db_client: TestClient, real_db_session: Session) -> None:
    """Title must be 3-120 characters and description at most 2000."""
    _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    _login(real_db_client, "inst@test.edu")

    # Short title
    resp_short = real_db_client.post("/api/courses", json={"title": "ab"})
    assert resp_short.status_code == 422

    # Long title
    resp_long = real_db_client.post("/api/courses", json={"title": "a" * 121})
    assert resp_long.status_code == 422

    # Long description
    resp_desc = real_db_client.post(
        "/api/courses",
        json={"title": "Valid Title", "description": "d" * 2001},
    )
    assert resp_desc.status_code == 422


def test_draft_course_visibility_and_admin_access(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Drafts return 404 to non-owners; owners and admin can access."""
    inst1 = _create_user(real_db_session, "owner@test.edu", UserRole.INSTRUCTOR)
    _create_user(real_db_session, "other@test.edu", UserRole.INSTRUCTOR)
    _create_user(real_db_session, "stud@test.edu", UserRole.STUDENT)
    _create_user(real_db_session, "admin@test.edu", UserRole.ADMIN)

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
    _login(real_db_client, "other@test.edu")
    assert real_db_client.get(f"/api/courses/{course.id}").status_code == 404

    # Student -> 404
    _login(real_db_client, "stud@test.edu")
    assert real_db_client.get(f"/api/courses/{course.id}").status_code == 404

    # Owner -> 200
    _login(real_db_client, "owner@test.edu")
    resp_owner = real_db_client.get(f"/api/courses/{course.id}")
    assert resp_owner.status_code == 200
    assert resp_owner.json()["title"] == "Draft Course"

    # Admin -> 200
    _login(real_db_client, "admin@test.edu")
    resp_admin = real_db_client.get(f"/api/courses/{course.id}")
    assert resp_admin.status_code == 200


def test_course_update_and_status_transition_rules(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Owner/admin can update; publishing works; published to draft returns 409."""
    inst = _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    _create_user(real_db_session, "other@test.edu", UserRole.INSTRUCTOR)
    _create_user(real_db_session, "admin@test.edu", UserRole.ADMIN)

    course = Course(
        instructor_id=inst.id,
        title="Original Title",
        description="Original Desc",
        status=CourseStatus.DRAFT,
    )
    real_db_session.add(course)
    real_db_session.commit()

    # Other instructor cannot edit -> 403
    _login(real_db_client, "other@test.edu")
    resp_other = real_db_client.patch(
        f"/api/courses/{course.id}",
        json={"title": "Hacked Title"},
    )
    assert resp_other.status_code == 403

    # Owner publishes course
    _login(real_db_client, "inst@test.edu")
    resp_pub = real_db_client.patch(
        f"/api/courses/{course.id}",
        json={"title": "Updated Title", "status": "published"},
    )
    assert resp_pub.status_code == 200
    assert resp_pub.json()["status"] == "published"
    assert resp_pub.json()["title"] == "Updated Title"

    # Attempt to revert from published to draft -> 409
    resp_conflict = real_db_client.patch(
        f"/api/courses/{course.id}",
        json={"status": "draft"},
    )
    assert resp_conflict.status_code == 409
    assert resp_conflict.json()["code"] == "INVALID_STATUS_TRANSITION"

    # Admin can update title of published course
    _login(real_db_client, "admin@test.edu")
    resp_admin = real_db_client.patch(
        f"/api/courses/{course.id}",
        json={"title": "Admin Modified Title"},
    )
    assert resp_admin.status_code == 200
    assert resp_admin.json()["title"] == "Admin Modified Title"


def test_course_search_and_pagination(real_db_client: TestClient, real_db_session: Session) -> None:
    """Course listing supports ?q= search, limit, offset, and admin sees drafts."""
    inst = _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    _create_user(real_db_session, "stud@test.edu", UserRole.STUDENT)
    _create_user(real_db_session, "admin@test.edu", UserRole.ADMIN)

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
    _login(real_db_client, "stud@test.edu")
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
    _login(real_db_client, "admin@test.edu")
    resp_admin = real_db_client.get("/api/courses?q=Python")
    assert resp_admin.status_code == 200
    assert resp_admin.json()["total"] == 6


def test_enrolled_flag_is_per_student_and_my_courses(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """The enrolled flag in listing is per student and my courses returns enrolled."""
    inst = _create_user(real_db_session, "inst@test.edu", UserRole.INSTRUCTOR)
    s1 = _create_user(real_db_session, "s1@test.edu", UserRole.STUDENT)
    _create_user(real_db_session, "s2@test.edu", UserRole.STUDENT)

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
    _login(real_db_client, "s1@test.edu")
    r1 = real_db_client.get("/api/courses").json()
    assert r1["items"][0]["enrolled"] is True

    # s1 my-courses returns 1 course
    s1_courses = real_db_client.get("/api/students/me/courses").json()
    assert len(s1_courses) == 1
    assert s1_courses[0]["id"] == course.id

    # s2 sees enrolled == False
    _login(real_db_client, "s2@test.edu")
    r2 = real_db_client.get("/api/courses").json()
    assert r2["items"][0]["enrolled"] is False

    # s2 my-courses returns 0 courses
    s2_courses = real_db_client.get("/api/students/me/courses").json()
    assert len(s2_courses) == 0

    # Instructor my-courses includes enrolled_count == 1
    _login(real_db_client, "inst@test.edu")
    inst_courses = real_db_client.get("/api/instructors/me/courses").json()
    assert len(inst_courses) == 1
    assert inst_courses[0]["enrolled_count"] == 1
