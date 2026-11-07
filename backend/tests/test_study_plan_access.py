"""Access controls, days validation, isolation, and query bounds for study plan."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.internship import Internship, InternshipStatus
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user


def test_study_plan_role_guards(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Only authenticated students may access the study plan; others get 401 or 403."""
    # Anonymous request
    anon_resp = real_db_client.get("/api/students/me/study-plan")
    assert anon_resp.status_code == 401

    # Disallowed roles
    for role, email in [
        (UserRole.INSTRUCTOR, "inst_guard_sp@example.com"),
        (UserRole.ORGANIZATION, "org_guard_sp@example.com"),
        (UserRole.COORDINATOR, "coord_guard_sp@example.com"),
        (UserRole.ADMIN, "admin_guard_sp@example.com"),
    ]:
        create_test_user(db=real_db_session, email=email, role=role)
        login_test_user(real_db_client, email)
        resp = real_db_client.get("/api/students/me/study-plan")
        assert resp.status_code == 403, f"Expected 403 for {role}, got {resp.status_code}"

    # Student role succeeds
    create_test_user(db=real_db_session, email="stu_guard_sp@example.com", role=UserRole.STUDENT)
    login_test_user(real_db_client, "stu_guard_sp@example.com")
    resp_student = real_db_client.get("/api/students/me/study-plan")
    assert resp_student.status_code == 200


def test_study_plan_days_validation(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Days parameter accepts 3 through 14 inclusive, rejecting 2 and 15."""
    create_test_user(db=real_db_session, email="stu_days_val@example.com", role=UserRole.STUDENT)
    login_test_user(real_db_client, "stu_days_val@example.com")

    # Boundary rejections: 2 and 15
    assert real_db_client.get("/api/students/me/study-plan?days=2").status_code == 422
    assert real_db_client.get("/api/students/me/study-plan?days=15").status_code == 422

    # Boundary acceptances: 3 and 14
    resp_3 = real_db_client.get("/api/students/me/study-plan?days=3")
    assert resp_3.status_code == 200
    assert resp_3.json()["window"]["days"] == 3
    assert len(resp_3.json()["plan"]) == 3

    resp_14 = real_db_client.get("/api/students/me/study-plan?days=14")
    assert resp_14.status_code == 200
    assert resp_14.json()["window"]["days"] == 14
    assert len(resp_14.json()["plan"]) == 14


def test_study_plan_student_isolation(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """A student's study plan strictly isolates coursework from other students."""
    student_a = create_test_user(
        db=real_db_session, email="stu_iso_a@example.com", role=UserRole.STUDENT
    )
    student_b = create_test_user(
        db=real_db_session, email="stu_iso_b@example.com", role=UserRole.STUDENT
    )
    instructor = create_test_user(
        db=real_db_session, email="inst_iso_sp@example.com", role=UserRole.INSTRUCTOR
    )

    course_a = Course(
        instructor_id=instructor.id,
        title="Course A For Student A",
        description="Course A",
        status=CourseStatus.PUBLISHED,
    )
    course_b = Course(
        instructor_id=instructor.id,
        title="Course B For Student B",
        description="Course B",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add_all([course_a, course_b])
    real_db_session.commit()

    real_db_session.add_all(
        [
            Enrollment(student_id=student_a.id, course_id=course_a.id),
            Enrollment(student_id=student_b.id, course_id=course_b.id),
            Assignment(
                course_id=course_a.id,
                title="Private Task A",
                description="Task A",
                due_at=datetime.now(UTC) + timedelta(days=2),
                max_points=30,
            ),
            Assignment(
                course_id=course_b.id,
                title="Private Task B",
                description="Task B",
                due_at=datetime.now(UTC) + timedelta(days=2),
                max_points=30,
            ),
        ]
    )
    real_db_session.commit()

    # Query as student A: must see Course A, never Course B
    login_test_user(real_db_client, "stu_iso_a@example.com")
    resp_a = real_db_client.get("/api/students/me/study-plan")
    assert resp_a.status_code == 200
    titles_a = [i["title"] for day in resp_a.json()["plan"] for i in day["items"]]
    assert "Private Task A" in titles_a
    assert "Private Task B" not in titles_a


def test_study_plan_profile_hint_and_query_count_bound(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Incomplete profile shows hint on internship item; total queries remain bounded."""
    student = create_test_user(
        db=real_db_session, email="stu_hint_sp@example.com", role=UserRole.STUDENT
    )
    # Ensure profile is incomplete (blank university/department)
    prof = real_db_session.scalar(
        StudentProfile.__table__.select().where(StudentProfile.user_id == student.id)
    )
    if not prof:
        real_db_session.add(
            StudentProfile(
                user_id=student.id,
                university="",
                department="",
                skills=["Python", "FastAPI"],
            )
        )
        real_db_session.commit()

    org = create_test_user(
        db=real_db_session, email="org_hint_sp@example.com", role=UserRole.ORGANIZATION
    )
    real_db_session.add(
        OrganizationProfile(
            user_id=org.id,
            organization_name="Innovate Ltd",
            approval_status=ApprovalStatus.APPROVED,
        )
    )
    real_db_session.commit()

    # Create open internship with matching deadline in window
    internship = Internship(
        organization_id=org.id,
        title="Backend Software Intern",
        description="Python FastAPI backend engineering.",
        requirements="Python FastAPI skills.",
        location="Remote",
        work_mode="remote",
        status=InternshipStatus.OPEN,
        application_deadline=datetime.now(UTC) + timedelta(days=3),
    )
    real_db_session.add(internship)
    real_db_session.commit()

    login_test_user(real_db_client, "stu_hint_sp@example.com")

    # Measure database query count during endpoint execution
    queries: list[str] = []

    def count_query(
        _conn: object,
        _cursor: object,
        statement: str,
        _parameters: object,
        _context: object,
        _executemany: object,
    ) -> None:
        queries.append(statement)

    engine = real_db_session.get_bind()
    event.listen(engine, "before_cursor_execute", count_query)
    try:
        resp = real_db_client.get("/api/students/me/study-plan?days=7")
    finally:
        event.remove(engine, "before_cursor_execute", count_query)

    assert resp.status_code == 200
    data = resp.json()

    # Query count bound: must execute <= 15 database statements
    assert len(queries) <= 15, f"Query count exceeded bound: {len(queries)} > 15"

    # Find the internship item in the plan
    all_items = [i for day in data["plan"] for i in day["items"]]
    internship_items = [i for i in all_items if i["type"] == "internship"]
    assert len(internship_items) >= 1
    target_item = internship_items[0]
    assert "Complete your profile to apply" in target_item["reason"]
    assert "profile_incomplete" in target_item["flags"]
