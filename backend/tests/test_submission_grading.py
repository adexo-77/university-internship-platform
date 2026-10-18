"""Integration tests for assignment submissions roster isolation and grading permissions."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import UserRole
from tests.conftest import create_test_user, login_test_user, seed_course_and_assignment


def test_student_isolation_and_submissions_roster(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Students cannot view others' work; owner instructor/admin sees every student with status."""
    inst = create_test_user(real_db_session, "inst_roster@test.edu", UserRole.INSTRUCTOR)
    other_inst = create_test_user(real_db_session, "other_inst_r@test.edu", UserRole.INSTRUCTOR)
    admin = create_test_user(real_db_session, "admin_r@test.edu", UserRole.ADMIN)
    stud1 = create_test_user(real_db_session, "s1@test.edu", UserRole.STUDENT, full_name="Alice")
    stud2 = create_test_user(real_db_session, "s2@test.edu", UserRole.STUDENT, full_name="Bob")

    course, assignment = seed_course_and_assignment(real_db_session, inst)
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
    login_test_user(real_db_client, stud1.email)
    res = real_db_client.get(f"/api/assignments/{assignment.id}/submission")
    assert res.status_code == 200
    assert res.json()["content"] == "Alice's submission"

    # Bob views his own submission -> 404
    login_test_user(real_db_client, stud2.email)
    res = real_db_client.get(f"/api/assignments/{assignment.id}/submission")
    assert res.status_code == 404

    # Students cannot access all submissions -> 403
    res = real_db_client.get(f"/api/assignments/{assignment.id}/submissions")
    assert res.status_code == 403

    # Other instructor gets 404
    login_test_user(real_db_client, other_inst.email)
    res = real_db_client.get(f"/api/assignments/{assignment.id}/submissions")
    assert res.status_code == 404

    # Owner instructor sees both students: Alice with submission, Bob with None
    login_test_user(real_db_client, inst.email)
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
    login_test_user(real_db_client, admin.email)
    res_admin = real_db_client.get(f"/api/assignments/{assignment.id}/submissions")
    assert res_admin.status_code == 200
    assert len(res_admin.json()) == 2


def test_grading_permissions_and_bounds(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Owner instructor can grade/regrade; admin (read-only) and others get 403; bounds enforced."""
    inst = create_test_user(real_db_session, "inst_grade_p@test.edu", UserRole.INSTRUCTOR)
    other_inst = create_test_user(real_db_session, "other_inst_g@test.edu", UserRole.INSTRUCTOR)
    admin = create_test_user(real_db_session, "admin_g@test.edu", UserRole.ADMIN)
    stud = create_test_user(real_db_session, "stud_g@test.edu", UserRole.STUDENT)

    course, assignment = seed_course_and_assignment(real_db_session, inst, max_points=100)
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
    login_test_user(real_db_client, stud.email)
    res = real_db_client.put(f"/api/submissions/{sub.id}/grade", json={"grade": 90})
    assert res.status_code == 403

    # Admin has read-only access, cannot grade -> 403
    login_test_user(real_db_client, admin.email)
    res = real_db_client.put(f"/api/submissions/{sub.id}/grade", json={"grade": 90})
    assert res.status_code == 403

    # Other instructor cannot grade -> 403
    login_test_user(real_db_client, other_inst.email)
    res = real_db_client.put(f"/api/submissions/{sub.id}/grade", json={"grade": 90})
    assert res.status_code == 403

    # Owner instructor cannot grade exceeding max_points (101 > 100) -> 409
    login_test_user(real_db_client, inst.email)
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
