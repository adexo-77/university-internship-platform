"""Integration tests for assignment submission lifecycle, late calculation, and locking."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.models.user import UserRole
from tests.factories import create_test_user, login_test_user, seed_course_and_assignment


def test_submission_lifecycle_and_late_calculation(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """On-time submission computes is_late=False; past-due submission computes is_late=True."""
    inst = create_test_user(real_db_session, "inst_sub@test.edu", UserRole.INSTRUCTOR)
    stud1 = create_test_user(real_db_session, "stud1@test.edu", UserRole.STUDENT)
    stud2 = create_test_user(real_db_session, "stud2@test.edu", UserRole.STUDENT)

    course, assignment = seed_course_and_assignment(real_db_session, inst, due_delta_days=2)
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud1.id))
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud2.id))
    real_db_session.commit()

    # 1. stud1 submits before deadline -> is_late = False
    login_test_user(real_db_client, stud1.email)
    res = real_db_client.put(
        f"/api/assignments/{assignment.id}/submission",
        json={"content": "My graph solution", "link_url": "https://github.com/stud1/repo"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_late"] is False
    assert data["content"] == "My graph solution"
    assert data["link_url"] == "https://github.com/stud1/repo"

    # Resubmission before grading works
    res_update = real_db_client.put(
        f"/api/assignments/{assignment.id}/submission",
        json={"content": "Updated graph solution"},
    )
    assert res_update.status_code == 200
    assert res_update.json()["content"] == "Updated graph solution"

    # 2. Adjust assignment.due_at to the past in DB to test deterministic late calculation
    assignment.due_at = datetime.now(UTC) - timedelta(hours=2)
    real_db_session.commit()

    # stud2 submits after deadline -> is_late = True
    login_test_user(real_db_client, stud2.email)
    res_late = real_db_client.put(
        f"/api/assignments/{assignment.id}/submission",
        json={"content": "Late submission solution"},
    )
    assert res_late.status_code == 200
    assert res_late.json()["is_late"] is True


def test_submission_locked_once_graded_and_validation(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Submissions cannot be modified once graded, extra/invalid fields rejected."""
    inst = create_test_user(real_db_session, "inst_grade@test.edu", UserRole.INSTRUCTOR)
    stud = create_test_user(real_db_session, "stud_locked@test.edu", UserRole.STUDENT)
    course, assignment = seed_course_and_assignment(real_db_session, inst, due_delta_days=3)
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud.id))
    real_db_session.commit()

    login_test_user(real_db_client, stud.email)

    # Extra fields rejected -> 422
    res = real_db_client.put(
        f"/api/assignments/{assignment.id}/submission",
        json={"content": "Work", "is_late": False, "student_id": 99},
    )
    assert res.status_code == 422

    # Invalid URL scheme -> 422
    res = real_db_client.put(
        f"/api/assignments/{assignment.id}/submission",
        json={"content": "Work", "link_url": "ftp://not-http.com"},
    )
    assert res.status_code == 422

    # Submit valid work
    res = real_db_client.put(
        f"/api/assignments/{assignment.id}/submission",
        json={"content": "First valid draft"},
    )
    assert res.status_code == 200
    submission_id = res.json()["id"]

    # Instructor grades submission
    login_test_user(real_db_client, inst.email)
    res_grade = real_db_client.put(
        f"/api/submissions/{submission_id}/grade",
        json={"grade": 95, "feedback": "Excellent work!"},
    )
    assert res_grade.status_code == 200

    # Student attempts to resubmit -> 409
    login_test_user(real_db_client, stud.email)
    res_conflict = real_db_client.put(
        f"/api/assignments/{assignment.id}/submission",
        json={"content": "Sneaky resubmission after grading"},
    )
    assert res_conflict.status_code == 409
