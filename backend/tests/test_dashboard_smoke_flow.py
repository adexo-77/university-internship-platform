"""End-to-end backend smoke test exercising full flow and all four dashboards."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.application import ApplicationStatus
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.internship import InternshipStatus
from app.models.organization_profile import ApprovalStatus
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


def test_dashboard_full_lifecycle_smoke(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Smoke test: Provision full lifecycle then verify student, instructor,
    organization, and admin role dashboards.
    """
    # 1. Provision users
    admin = create_test_user(real_db_session, "smoke_admin@test.com", UserRole.ADMIN)
    instructor = create_test_user(real_db_session, "smoke_instructor@test.com", UserRole.INSTRUCTOR)
    student, _ = create_test_student(
        real_db_session, "smoke_student@test.com", university="Tech University"
    )
    org_user, _ = create_test_organization(
        real_db_session,
        "smoke_org@test.com",
        organization_name="Nexus Labs",
        approval_status=ApprovalStatus.APPROVED,
    )

    # 2. Instructor creates course & assignments
    course = Course(
        instructor_id=instructor.id,
        title="Distributed Systems",
        status=CourseStatus.PUBLISHED,
    )
    real_db_session.add(course)
    real_db_session.commit()

    now = datetime.now(UTC)
    a1 = Assignment(
        course_id=course.id,
        title="Raft Consensus",
        due_at=now - timedelta(days=2),
        max_points=100,
    )
    a2 = Assignment(
        course_id=course.id,
        title="Vector Clocks",
        due_at=now + timedelta(days=4),
        max_points=50,
    )
    real_db_session.add_all([a1, a2])
    real_db_session.commit()

    # 3. Student enrolls & submits work
    real_db_session.add(Enrollment(course_id=course.id, student_id=student.id))
    real_db_session.commit()

    # Submission 1 graded
    s1 = Submission(
        assignment_id=a1.id,
        student_id=student.id,
        content="Implementation done",
        is_late=False,
        grade=95,
        graded_at=now - timedelta(days=1),
    )
    real_db_session.add(s1)
    real_db_session.commit()

    # 4. Organization creates internship and student applies
    posting = create_test_internship(
        real_db_session,
        org_user,
        title="Cloud Infrastructure Intern",
        status=InternshipStatus.OPEN,
    )
    create_test_application(
        real_db_session,
        posting,
        student,
        status=ApplicationStatus.SHORTLISTED,
    )

    # 5. Verify Student Dashboard
    login_test_user(real_db_client, student.email)
    res_stud = real_db_client.get("/api/dashboard/student")
    assert res_stud.status_code == 200
    stud_data = res_stud.json()
    assert len(stud_data["due_next"]) == 1
    assert stud_data["due_next"][0]["title"] == "Vector Clocks"
    assert len(stud_data["recent_grades"]) == 1
    assert stud_data["recent_grades"][0]["grade"] == 95
    assert stud_data["courses"][0]["instructor_name"] == instructor.full_name
    assert stud_data["applications"]["counts_by_status"]["shortlisted"] == 1
    assert len(stud_data["applications"]["recent"]) == 1
    assert stud_data["applications"]["recent"][0]["id"] is not None

    # 6. Verify Instructor Dashboard
    login_test_user(real_db_client, instructor.email)
    res_inst = real_db_client.get("/api/dashboard/instructor")
    assert res_inst.status_code == 200
    inst_data = res_inst.json()
    assert len(inst_data["courses"]) == 1
    assert inst_data["courses"][0]["enrolled_count"] == 1
    assert inst_data["courses"][0]["submissions_awaiting_grading"] == 0

    # 7. Verify Organization Dashboard
    login_test_user(real_db_client, org_user.email)
    res_org = real_db_client.get("/api/dashboard/organization")
    assert res_org.status_code == 200
    org_data = res_org.json()
    assert org_data["approval_status"] == "approved"
    assert org_data["postings"]["counts_by_status"]["open"] >= 1
    assert org_data["postings"]["total"] >= 1
    assert len(org_data["recent_applications"]) == 1
    assert org_data["recent_applications"][0]["posting_title"] == "Cloud Infrastructure Intern"

    # 8. Verify Admin Dashboard
    login_test_user(real_db_client, admin.email)
    res_admin = real_db_client.get("/api/dashboard/admin")
    assert res_admin.status_code == 200
    admin_data = res_admin.json()
    assert admin_data["users_total_count"] >= 4
    assert admin_data["users_active_count"] >= 4
    assert admin_data["open_internships"] >= 1
    assert admin_data["applications_by_status"]["shortlisted"] >= 1
