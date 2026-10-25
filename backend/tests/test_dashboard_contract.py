"""Contract tests ensuring backend dashboard payloads match frontend fixtures."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

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

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "frontend" / "src" / "test" / "fixtures"


def extract_key_structure(data: Any) -> Any:
    """Extract recursive dictionary keys ignoring scalar values and array lengths."""
    if isinstance(data, dict):
        return {k: extract_key_structure(v) for k, v in sorted(data.items())}
    if isinstance(data, list):
        return [extract_key_structure(data[0])] if data else []
    return None


def load_fixture(filename: str) -> dict[str, Any]:
    with open(FIXTURES_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def test_student_dashboard_matches_frontend_contract(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    student, _ = create_test_student(real_db_session, "contract_stud@test.com")
    inst = create_test_user(real_db_session, "contract_inst@test.com", UserRole.INSTRUCTOR)
    org, _ = create_test_organization(
        real_db_session, "contract_org@test.com", approval_status=ApprovalStatus.APPROVED
    )

    course = Course(
        instructor_id=inst.id, title="Distributed Systems", status=CourseStatus.PUBLISHED
    )
    real_db_session.add(course)
    real_db_session.commit()
    real_db_session.add(Enrollment(course_id=course.id, student_id=student.id))
    real_db_session.commit()

    now = datetime.now(UTC)
    a1 = Assignment(
        course_id=course.id, title="Raft Consensus", due_at=now - timedelta(days=2), max_points=100
    )
    a2 = Assignment(
        course_id=course.id, title="Vector Clocks", due_at=now + timedelta(days=4), max_points=50
    )
    real_db_session.add_all([a1, a2])
    real_db_session.commit()

    sub = Submission(
        assignment_id=a1.id,
        student_id=student.id,
        content="done",
        grade=95,
        graded_at=now - timedelta(days=1),
    )
    real_db_session.add(sub)

    posting = create_test_internship(
        real_db_session, org, title="Cloud Infrastructure Intern", status=InternshipStatus.OPEN
    )
    create_test_application(real_db_session, posting, student, status=ApplicationStatus.SHORTLISTED)
    real_db_session.commit()

    login_test_user(real_db_client, student.email)
    res = real_db_client.get("/api/dashboard/student")
    assert res.status_code == 200

    fixture = load_fixture("dashboard_student.json")
    assert extract_key_structure(res.json()) == extract_key_structure(fixture)


def test_instructor_dashboard_matches_frontend_contract(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    inst = create_test_user(real_db_session, "contract_inst2@test.com", UserRole.INSTRUCTOR)
    student, _ = create_test_student(real_db_session, "contract_stud2@test.com")

    course = Course(
        instructor_id=inst.id, title="Distributed Systems", status=CourseStatus.PUBLISHED
    )
    real_db_session.add(course)
    real_db_session.commit()
    real_db_session.add(Enrollment(course_id=course.id, student_id=student.id))
    now = datetime.now(UTC)
    a = Assignment(
        course_id=course.id, title="Vector Clocks", due_at=now - timedelta(days=1), max_points=100
    )
    real_db_session.add(a)
    real_db_session.commit()

    sub = Submission(
        assignment_id=a.id,
        student_id=student.id,
        content="late work",
        is_late=True,
        submitted_at=now,
    )
    real_db_session.add(sub)
    real_db_session.commit()

    login_test_user(real_db_client, inst.email)
    res = real_db_client.get("/api/dashboard/instructor")
    assert res.status_code == 200

    fixture = load_fixture("dashboard_instructor.json")
    assert extract_key_structure(res.json()) == extract_key_structure(fixture)


def test_organization_and_admin_match_frontend_contract(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    admin = create_test_user(real_db_session, "contract_admin@test.com", UserRole.ADMIN)
    org, _ = create_test_organization(
        real_db_session, "contract_org2@test.com", approval_status=ApprovalStatus.APPROVED
    )
    student, _ = create_test_student(real_db_session, "contract_stud3@test.com")

    p = create_test_internship(
        real_db_session, org, title="Cloud Infrastructure Intern", status=InternshipStatus.OPEN
    )
    create_test_application(real_db_session, p, student, status=ApplicationStatus.SUBMITTED)
    real_db_session.commit()

    login_test_user(real_db_client, org.email)
    res_org = real_db_client.get("/api/dashboard/organization")
    assert res_org.status_code == 200

    org_fixture = load_fixture("dashboard_organization.json")
    assert extract_key_structure(res_org.json()) == extract_key_structure(org_fixture)

    login_test_user(real_db_client, admin.email)
    res_admin = real_db_client.get("/api/dashboard/admin")
    assert res_admin.status_code == 200

    admin_fixture = load_fixture("dashboard_admin.json")
    assert extract_key_structure(res_admin.json()) == extract_key_structure(admin_fixture)


def test_coordinator_dashboard_matches_frontend_contract(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    coord = create_test_user(real_db_session, "contract_coord@test.com", UserRole.COORDINATOR)
    org, _ = create_test_organization(
        real_db_session, "contract_org3@test.com", approval_status=ApprovalStatus.APPROVED
    )
    student, _ = create_test_student(real_db_session, "contract_stud4@test.com")

    p = create_test_internship(
        real_db_session, org, title="Backend Intern", status=InternshipStatus.OPEN
    )
    create_test_application(real_db_session, p, student, status=ApplicationStatus.SUBMITTED)
    real_db_session.commit()

    login_test_user(real_db_client, coord.email)
    res_coord = real_db_client.get("/api/dashboard/coordinator")
    assert res_coord.status_code == 200

    coord_fixture = load_fixture("dashboard_coordinator.json")
    assert extract_key_structure(res_coord.json()) == extract_key_structure(coord_fixture)


def test_contract_drift_detection_fails_on_renamed_or_missing_keys() -> None:
    """Drift check raises AssertionError when keys are renamed or missing."""
    base = {"courses": [{"id": 1, "title": "Math"}], "total": 1}
    renamed = {"courses": [{"course_id": 1, "title": "Math"}], "total": 1}
    missing = {"courses": [{"title": "Math"}], "total": 1}

    assert extract_key_structure(base) != extract_key_structure(renamed)
    assert extract_key_structure(base) != extract_key_structure(missing)
