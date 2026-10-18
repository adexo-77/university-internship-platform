"""Integration tests for assignment submissions, late computation, and grading."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.assignment import Assignment
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import User, UserRole


def _create_user(
    db: Session,
    email: str,
    role: UserRole,
    password: str = "Password123!",
    full_name: str = "Test User",
) -> User:
    """Helper to seed a user directly in the database."""
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


def _seed_course_and_assignment(
    db: Session,
    instructor: User,
    due_delta_days: int = 5,
    max_points: int = 100,
) -> tuple[Course, Assignment]:
    course = Course(
        instructor_id=instructor.id,
        title="Algorithms",
        description="Data structures & algos",
        status=CourseStatus.PUBLISHED,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    assignment = Assignment(
        course_id=course.id,
        title="Problem Set 1",
        description="Graph theory",
        due_at=datetime.now(UTC) + timedelta(days=due_delta_days),
        max_points=max_points,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return course, assignment


def test_submission_lifecycle_and_late_calculation(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """On-time submission computes is_late=False; past-due submission computes is_late=True."""
    inst = _create_user(real_db_session, "inst_sub@test.edu", UserRole.INSTRUCTOR)
    stud1 = _create_user(real_db_session, "stud1@test.edu", UserRole.STUDENT)
    stud2 = _create_user(real_db_session, "stud2@test.edu", UserRole.STUDENT)

    course, assignment = _seed_course_and_assignment(real_db_session, inst, due_delta_days=2)
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud1.id))
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud2.id))
    real_db_session.commit()

    # 1. stud1 submits before deadline -> is_late = False
    _login(real_db_client, stud1.email)
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
    _login(real_db_client, stud2.email)
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
    inst = _create_user(real_db_session, "inst_grade@test.edu", UserRole.INSTRUCTOR)
    stud = _create_user(real_db_session, "stud_locked@test.edu", UserRole.STUDENT)
    course, assignment = _seed_course_and_assignment(real_db_session, inst, due_delta_days=3)
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud.id))
    real_db_session.commit()

    _login(real_db_client, stud.email)

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
    _login(real_db_client, inst.email)
    res_grade = real_db_client.put(
        f"/api/submissions/{submission_id}/grade",
        json={"grade": 95, "feedback": "Excellent work!"},
    )
    assert res_grade.status_code == 200

    # Student attempts to resubmit -> 409
    _login(real_db_client, stud.email)
    res_conflict = real_db_client.put(
        f"/api/assignments/{assignment.id}/submission",
        json={"content": "Sneaky resubmission after grading"},
    )
    assert res_conflict.status_code == 409


def test_student_isolation_and_submissions_roster(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Students cannot view others' work; owner instructor/admin sees every student with status."""
    inst = _create_user(real_db_session, "inst_roster@test.edu", UserRole.INSTRUCTOR)
    other_inst = _create_user(real_db_session, "other_inst_r@test.edu", UserRole.INSTRUCTOR)
    admin = _create_user(real_db_session, "admin_r@test.edu", UserRole.ADMIN)
    stud1 = _create_user(real_db_session, "s1@test.edu", UserRole.STUDENT, full_name="Alice")
    stud2 = _create_user(real_db_session, "s2@test.edu", UserRole.STUDENT, full_name="Bob")

    course, assignment = _seed_course_and_assignment(real_db_session, inst)
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud1.id))
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud2.id))
    real_db_session.commit()

    # Only Alice submits
    sub1 = Submission(
        assignment_id=assignment.id,
        student_id=stud1.id,
        content="Alice's submission",
    )
    real_db_session.add(sub1)
    real_db_session.commit()

    # Alice views her own submission -> 200
    _login(real_db_client, stud1.email)
    res = real_db_client.get(f"/api/assignments/{assignment.id}/submission")
    assert res.status_code == 200
    assert res.json()["content"] == "Alice's submission"

    # Bob views his own submission -> 404
    _login(real_db_client, stud2.email)
    res = real_db_client.get(f"/api/assignments/{assignment.id}/submission")
    assert res.status_code == 404

    # Students cannot access all submissions -> 403
    res = real_db_client.get(f"/api/assignments/{assignment.id}/submissions")
    assert res.status_code == 403

    # Other instructor gets 404
    _login(real_db_client, other_inst.email)
    res = real_db_client.get(f"/api/assignments/{assignment.id}/submissions")
    assert res.status_code == 404

    # Owner instructor sees both students: Alice with submission, Bob with None
    _login(real_db_client, inst.email)
    res = real_db_client.get(f"/api/assignments/{assignment.id}/submissions")
    assert res.status_code == 200
    roster = res.json()
    assert len(roster) == 2

    alice_entry = next(r for r in roster if r["student_id"] == stud1.id)
    bob_entry = next(r for r in roster if r["student_id"] == stud2.id)

    assert alice_entry["submission"] is not None
    assert alice_entry["submission"]["content"] == "Alice's submission"
    assert bob_entry["submission"] is None

    # Admin also has read-only roster access
    _login(real_db_client, admin.email)
    res_admin = real_db_client.get(f"/api/assignments/{assignment.id}/submissions")
    assert res_admin.status_code == 200
    assert len(res_admin.json()) == 2


def test_grading_permissions_and_bounds(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Owner instructor can grade/regrade; admin (read-only) and others get 403; bounds enforced."""
    inst = _create_user(real_db_session, "inst_grade_p@test.edu", UserRole.INSTRUCTOR)
    other_inst = _create_user(real_db_session, "other_inst_g@test.edu", UserRole.INSTRUCTOR)
    admin = _create_user(real_db_session, "admin_g@test.edu", UserRole.ADMIN)
    stud = _create_user(real_db_session, "stud_g@test.edu", UserRole.STUDENT)

    course, assignment = _seed_course_and_assignment(real_db_session, inst, max_points=100)
    real_db_session.add(Enrollment(course_id=course.id, student_id=stud.id))
    real_db_session.commit()

    sub = Submission(
        assignment_id=assignment.id,
        student_id=stud.id,
        content="Ready for grading",
    )
    real_db_session.add(sub)
    real_db_session.commit()
    real_db_session.refresh(sub)

    # Student cannot grade -> 403
    _login(real_db_client, stud.email)
    res = real_db_client.put(f"/api/submissions/{sub.id}/grade", json={"grade": 90})
    assert res.status_code == 403

    # Admin has read-only access, cannot grade -> 403
    _login(real_db_client, admin.email)
    res = real_db_client.put(f"/api/submissions/{sub.id}/grade", json={"grade": 90})
    assert res.status_code == 403

    # Other instructor cannot grade -> 403
    _login(real_db_client, other_inst.email)
    res = real_db_client.put(f"/api/submissions/{sub.id}/grade", json={"grade": 90})
    assert res.status_code == 403

    # Owner instructor cannot grade exceeding max_points (101 > 100) -> 409
    _login(real_db_client, inst.email)
    res = real_db_client.put(f"/api/submissions/{sub.id}/grade", json={"grade": 105})
    assert res.status_code == 409

    # Owner instructor grades successfully -> 200
    res = real_db_client.put(
        f"/api/submissions/{sub.id}/grade",
        json={"grade": 88, "feedback": "Good effort"},
    )
    assert res.status_code == 200
    assert res.json()["grade"] == 88
    assert res.json()["feedback"] == "Good effort"

    # Regrading is permitted -> 200
    res_regrade = real_db_client.put(
        f"/api/submissions/{sub.id}/grade",
        json={"grade": 92, "feedback": "Revised after review"},
    )
    assert res_regrade.status_code == 200
    assert res_regrade.json()["grade"] == 92
    assert res_regrade.json()["feedback"] == "Revised after review"
