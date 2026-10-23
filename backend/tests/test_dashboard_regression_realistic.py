"""Regression tests for role dashboards with realistic data covering all statuses."""

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


def test_student_dashboard_realistic_statuses(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Student dashboard handles submitted, late, and graded work and all application statuses."""
    student, _ = create_test_student(real_db_session, "reg_stud@test.com")
    inst = create_test_user(real_db_session, "reg_inst@test.com", UserRole.INSTRUCTOR)
    org, _ = create_test_organization(
        real_db_session, "reg_org@test.com", approval_status=ApprovalStatus.APPROVED
    )

    course = Course(instructor_id=inst.id, title="Algorithms", status=CourseStatus.PUBLISHED)
    real_db_session.add(course)
    real_db_session.commit()
    real_db_session.add(Enrollment(course_id=course.id, student_id=student.id))
    real_db_session.commit()

    now = datetime.now(UTC)
    a_graded = Assignment(
        course_id=course.id, title="HW 1", due_at=now - timedelta(days=5), max_points=100
    )
    a_due = Assignment(
        course_id=course.id, title="HW 2", due_at=now + timedelta(days=3), max_points=50
    )
    real_db_session.add_all([a_graded, a_due])
    real_db_session.commit()

    # Graded submission (late=True)
    sub = Submission(
        assignment_id=a_graded.id,
        student_id=student.id,
        content="hw1 code",
        is_late=True,
        grade=92,
        graded_at=now - timedelta(days=2),
    )
    real_db_session.add(sub)

    # Postings & applications in every status: submitted, shortlisted, accepted, rejected, withdrawn
    create_test_internship(real_db_session, org, title="Dev Intern", status=InternshipStatus.OPEN)
    for st in [
        ApplicationStatus.SUBMITTED,
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.ACCEPTED,
        ApplicationStatus.REJECTED,
        ApplicationStatus.WITHDRAWN,
    ]:
        p = create_test_internship(
            real_db_session, org, title=f"Post {st.value}", status=InternshipStatus.OPEN
        )
        create_test_application(real_db_session, p, student, status=st)
    real_db_session.commit()

    login_test_user(real_db_client, student.email)
    res = real_db_client.get("/api/dashboard/student")
    assert res.status_code == 200
    data = res.json()

    assert len(data["due_next"]) == 1
    assert data["due_next"][0]["title"] == "HW 2"
    assert len(data["recent_grades"]) == 1
    assert data["recent_grades"][0]["grade"] == 92
    assert data["courses"][0]["instructor_name"] == inst.full_name
    assert data["applications"]["counts_by_status"]["submitted"] == 1
    assert data["applications"]["counts"]["submitted"] == 1
    assert len(data["applications"]["recent"]) >= 1
    assert data["applications"]["recent"][0]["application_id"] is not None
    assert data["profile_complete"] is True


def test_instructor_dashboard_realistic_statuses(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Instructor dashboard accurately reports awaiting grading counts and late flags."""
    inst = create_test_user(real_db_session, "reg_inst2@test.com", UserRole.INSTRUCTOR)
    s1, _ = create_test_student(real_db_session, "reg_s1@test.com")
    s2, _ = create_test_student(real_db_session, "reg_s2@test.com")

    course = Course(instructor_id=inst.id, title="Databases", status=CourseStatus.PUBLISHED)
    real_db_session.add(course)
    real_db_session.commit()
    real_db_session.add_all(
        [
            Enrollment(course_id=course.id, student_id=s1.id),
            Enrollment(course_id=course.id, student_id=s2.id),
        ]
    )
    now = datetime.now(UTC)
    assign = Assignment(
        course_id=course.id, title="Schema Design", due_at=now - timedelta(days=2), max_points=100
    )
    real_db_session.add(assign)
    real_db_session.commit()

    sub_ontime = Submission(
        assignment_id=assign.id,
        student_id=s1.id,
        content="sql 1",
        is_late=False,
        submitted_at=now - timedelta(days=3),
    )
    sub_late = Submission(
        assignment_id=assign.id,
        student_id=s2.id,
        content="sql 2",
        is_late=True,
        submitted_at=now - timedelta(days=1),
    )
    real_db_session.add_all([sub_ontime, sub_late])
    real_db_session.commit()

    login_test_user(real_db_client, inst.email)
    res = real_db_client.get("/api/dashboard/instructor")
    assert res.status_code == 200
    data = res.json()

    assert data["courses"][0]["submissions_awaiting_grading"] == 2
    assert data["courses"][0]["awaiting_grading_count"] == 2
    assert len(data["needs_grading"]) == 2
    assert data["needs_grading"][0]["late"] is False
    assert data["needs_grading"][0]["is_late"] is False
    assert data["needs_grading"][1]["late"] is True
    assert data["needs_grading"][1]["is_late"] is True


def test_organization_and_admin_dashboards_realistic_statuses(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Organization and admin dashboards cover postings in all 5 statuses and applications."""
    admin = create_test_user(real_db_session, "reg_adm@test.com", UserRole.ADMIN)
    org, _ = create_test_organization(
        real_db_session, "reg_org2@test.com", approval_status=ApprovalStatus.APPROVED
    )
    student, _ = create_test_student(real_db_session, "reg_stud2@test.com")

    # Postings in all 5 statuses: DRAFT, PENDING_REVIEW, OPEN, REJECTED, CLOSED
    create_test_internship(real_db_session, org, title="Draft Job", status=InternshipStatus.DRAFT)
    create_test_internship(
        real_db_session, org, title="Pending Job", status=InternshipStatus.PENDING_REVIEW
    )
    p_open = create_test_internship(
        real_db_session, org, title="Open Job", status=InternshipStatus.OPEN
    )
    create_test_internship(
        real_db_session, org, title="Rejected Job", status=InternshipStatus.REJECTED
    )
    create_test_internship(real_db_session, org, title="Closed Job", status=InternshipStatus.CLOSED)

    create_test_application(real_db_session, p_open, student, status=ApplicationStatus.SUBMITTED)

    login_test_user(real_db_client, org.email)
    res_org = real_db_client.get("/api/dashboard/organization")
    assert res_org.status_code == 200
    org_data = res_org.json()
    assert org_data["approval_status"] == "approved"
    assert org_data["postings"]["counts_by_status"]["draft"] >= 1
    assert org_data["postings"]["counts_by_status"]["pending_review"] >= 1
    assert org_data["postings"]["counts_by_status"]["open"] >= 1
    assert org_data["postings"]["counts_by_status"]["rejected"] >= 1
    assert org_data["postings"]["counts_by_status"]["closed"] >= 1
    assert org_data["posting_counts"]["open"] >= 1
    assert org_data["applications_awaiting_decision"] >= 1
    assert len(org_data["recent_applications"]) >= 1

    login_test_user(real_db_client, admin.email)
    res_admin = real_db_client.get("/api/dashboard/admin")
    assert res_admin.status_code == 200
    admin_data = res_admin.json()
    assert admin_data["users_active_count"] >= 3
    assert admin_data["active_users_count"] >= 3
    assert admin_data["postings_pending_review"] >= 1
    assert admin_data["internships_pending_review"] >= 1
    assert admin_data["open_internships"] >= 1
    assert admin_data["applications_by_status"]["submitted"] >= 1
