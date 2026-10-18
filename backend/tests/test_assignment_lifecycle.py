"""Integration tests for assignment update grade floor constraints and deletion guards."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import User, UserRole
from tests.factories import create_test_user, login_test_user


def _seed_course(
    db: Session, instructor: User, status: CourseStatus = CourseStatus.PUBLISHED
) -> Course:
    course = Course(
        instructor_id=instructor.id,
        title="Web Systems Architecture",
        description="Core computing",
        status=status,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


def test_assignment_patch_max_points_conflict_with_existing_grade(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """max_points cannot be dropped below an existing grade."""
    inst = create_test_user(real_db_session, "inst_patch@test.edu", UserRole.INSTRUCTOR)
    stud = create_test_user(real_db_session, "stud_patch@test.edu", UserRole.STUDENT)
    course = _seed_course(real_db_session, inst)
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud.id))
    assignment = Assignment(
        course_id=course.id,
        title="Project",
        due_at=datetime.now(UTC) + timedelta(days=5),
        max_points=100,
    )
    real_db_session.add(assignment)
    real_db_session.commit()
    real_db_session.refresh(assignment)

    # Seed an existing graded submission with 85
    sub = Submission(
        assignment_id=assignment.id,
        student_id=stud.id,
        content="Final project submission",
        grade=85,
        graded_at=datetime.now(UTC),
        graded_by=inst.id,
    )
    real_db_session.add(sub)
    real_db_session.commit()

    login_test_user(real_db_client, inst.email)

    # Attempt to lower max_points to 80 -> 409
    res = real_db_client.patch(
        f"/api/assignments/{assignment.id}",
        json={"max_points": 80},
    )
    assert res.status_code == 409

    # Lowering max_points to 90 is valid
    res = real_db_client.patch(
        f"/api/assignments/{assignment.id}",
        json={"max_points": 90, "title": "Updated Project Title"},
    )
    assert res.status_code == 200
    assert res.json()["max_points"] == 90
    assert res.json()["title"] == "Updated Project Title"


def test_assignment_delete_blocked_when_submissions_exist(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Deleting an assignment is forbidden with 409 if submissions exist."""
    inst = create_test_user(real_db_session, "inst_del@test.edu", UserRole.INSTRUCTOR)
    stud = create_test_user(real_db_session, "stud_del@test.edu", UserRole.STUDENT)
    course = _seed_course(real_db_session, inst)
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud.id))
    assignment = Assignment(
        course_id=course.id,
        title="Lab 1",
        due_at=datetime.now(UTC) + timedelta(days=5),
        max_points=50,
    )
    real_db_session.add(assignment)
    real_db_session.commit()
    real_db_session.refresh(assignment)

    sub = Submission(
        assignment_id=assignment.id,
        student_id=stud.id,
        content="Lab answers",
    )
    real_db_session.add(sub)
    real_db_session.commit()

    login_test_user(real_db_client, inst.email)

    # Deleting assignment with submission -> 409
    res = real_db_client.delete(f"/api/assignments/{assignment.id}")
    assert res.status_code == 409

    # Remove submission, then delete succeeds -> 204
    real_db_session.delete(sub)
    real_db_session.commit()

    res = real_db_client.delete(f"/api/assignments/{assignment.id}")
    assert res.status_code == 204

    # Subsequent get -> 404
    res = real_db_client.get(f"/api/assignments/{assignment.id}")
    assert res.status_code == 404
