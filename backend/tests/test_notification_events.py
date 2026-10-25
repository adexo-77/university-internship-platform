"""Tests for academic and application domain notification events."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.application import ApplicationStatus
from app.models.enrollment import Enrollment
from app.models.notification import Notification, NotificationKind
from app.models.student_profile import StudentProfile
from app.models.user import UserRole
from app.schemas.application import ApplicationCreate, ApplicationDecision
from app.schemas.assignment import AssignmentCreate
from app.schemas.submission import SubmissionGrade, SubmissionSubmit
from app.services.application import apply_to_internship, decide_application
from app.services.assignment import create_assignment
from app.services.submission import grade_submission, submit_assignment
from tests.factories import create_test_internship, create_test_user, seed_course_and_assignment


def test_assignment_created_notifies_enrolled_students_only(real_db_session: Session) -> None:
    """Creating an assignment notifies all enrolled students but not non-enrolled or instructor."""
    db = real_db_session
    inst = create_test_user(db, "inst_notif@example.com", UserRole.INSTRUCTOR)
    s1 = create_test_user(db, "s1_notif@example.com", UserRole.STUDENT)
    s2 = create_test_user(db, "s2_notif@example.com", UserRole.STUDENT)
    s3_not_enrolled = create_test_user(db, "s3_notif@example.com", UserRole.STUDENT)

    course, _ = seed_course_and_assignment(db, inst)
    db.add(Enrollment(course_id=course.id, student_id=s1.id))
    db.add(Enrollment(course_id=course.id, student_id=s2.id))
    db.commit()

    due = datetime.now(UTC) + timedelta(days=5)
    payload = AssignmentCreate(
        title="Distributed Systems Lab",
        description="Raft consensus implementation",
        due_at=due,
        max_points=100,
    )
    assignment = create_assignment(db, course.id, payload, inst)

    # Enrolled students received notification
    n1 = db.scalar(
        select(Notification).where(
            Notification.user_id == s1.id,
            Notification.kind == NotificationKind.ASSIGNMENT_CREATED,
        )
    )
    assert n1 is not None
    assert n1.title == f"New Assignment: {assignment.title}"
    assert n1.link_path == f"/assignments/{assignment.id}"

    n2 = db.scalar(
        select(Notification).where(
            Notification.user_id == s2.id,
            Notification.kind == NotificationKind.ASSIGNMENT_CREATED,
        )
    )
    assert n2 is not None

    # Non-enrolled student received nothing
    assert db.scalar(select(Notification).where(Notification.user_id == s3_not_enrolled.id)) is None
    # Instructor (actor) received nothing
    assert db.scalar(select(Notification).where(Notification.user_id == inst.id)) is None


def test_first_submission_notifies_instructor_and_updates_do_not(real_db_session: Session) -> None:
    """First submission notifies instructor; subsequent updates do not duplicate notification."""
    db = real_db_session
    inst = create_test_user(db, "inst_sub_notif@example.com", UserRole.INSTRUCTOR)
    student = create_test_user(db, "stud_sub_notif@example.com", UserRole.STUDENT)
    course, assignment = seed_course_and_assignment(db, inst)
    db.add(Enrollment(course_id=course.id, student_id=student.id))
    db.commit()

    # 1. First submission
    sub_payload = SubmissionSubmit(content="Initial solution code")
    submit_assignment(db, assignment.id, sub_payload, student)

    notifs = list(
        db.scalars(
            select(Notification).where(
                Notification.user_id == inst.id,
                Notification.kind == NotificationKind.FIRST_SUBMISSION,
            )
        )
    )
    assert len(notifs) == 1
    assert "submitted to" in notifs[0].message
    assert notifs[0].link_path == f"/assignments/{assignment.id}"

    # Student was not notified
    assert db.scalar(select(Notification).where(Notification.user_id == student.id)) is None

    # 2. Resubmission / update before grading
    sub_payload_v2 = SubmissionSubmit(content="Updated solution with tests")
    submit_assignment(db, assignment.id, sub_payload_v2, student)

    notifs_after = list(
        db.scalars(
            select(Notification).where(
                Notification.user_id == inst.id,
                Notification.kind == NotificationKind.FIRST_SUBMISSION,
            )
        )
    )
    assert len(notifs_after) == 1


def test_submission_graded_notifies_student(real_db_session: Session) -> None:
    """Grading notifies student with title and score; instructor is not notified."""
    db = real_db_session
    inst = create_test_user(db, "inst_grade_notif@example.com", UserRole.INSTRUCTOR)
    student = create_test_user(db, "stud_grade_notif@example.com", UserRole.STUDENT)
    course, assignment = seed_course_and_assignment(db, inst)
    db.add(Enrollment(course_id=course.id, student_id=student.id))
    db.commit()

    sub = submit_assignment(db, assignment.id, SubmissionSubmit(content="My homework"), student)
    grade_payload = SubmissionGrade(grade=95, feedback="Excellent algorithmic complexity.")
    grade_submission(db, sub.id, grade_payload, inst)

    notif = db.scalar(
        select(Notification).where(
            Notification.user_id == student.id,
            Notification.kind == NotificationKind.SUBMISSION_GRADED,
        )
    )
    assert notif is not None
    assert f"95/{assignment.max_points}" in notif.message
    assert assignment.title in notif.title
    assert notif.link_path == f"/assignments/{assignment.id}"

    # Instructor is not notified
    inst_graded_notifs = list(
        db.scalars(
            select(Notification).where(
                Notification.user_id == inst.id,
                Notification.kind == NotificationKind.SUBMISSION_GRADED,
            )
        )
    )
    assert len(inst_graded_notifs) == 0


def test_application_submission_notifies_organization(real_db_session: Session) -> None:
    """Student application notifies the posting organization; student is not notified."""
    db = real_db_session
    org = create_test_user(db, "org_app_notif@example.com", UserRole.ORGANIZATION)
    student = create_test_user(db, "stud_app_notif@example.com", UserRole.STUDENT)
    posting = create_test_internship(db, org, title="Backend Intern")

    prof = StudentProfile(user_id=student.id, university="AAU", department="SE")
    db.add(prof)
    db.commit()

    apply_to_internship(
        db,
        posting.id,
        student.id,
        ApplicationCreate(cover_letter="Passionate about high-throughput APIs."),
    )

    org_notif = db.scalar(
        select(Notification).where(
            Notification.user_id == org.id,
            Notification.kind == NotificationKind.APPLICATION_RECEIVED,
        )
    )
    assert org_notif is not None
    assert "New Application: Backend Intern" in org_notif.title
    assert org_notif.link_path == f"/internships/{posting.id}"

    # Student was not notified
    student_notifs = list(
        db.scalars(
            select(Notification).where(
                Notification.user_id == student.id,
                Notification.kind == NotificationKind.APPLICATION_RECEIVED,
            )
        )
    )
    assert len(student_notifs) == 0


def test_application_decision_notifies_student(real_db_session: Session) -> None:
    """Organization decision notifies the student with decision message; org is not notified."""
    db = real_db_session
    org = create_test_user(db, "org_dec_notif@example.com", UserRole.ORGANIZATION)
    student = create_test_user(db, "stud_dec_notif@example.com", UserRole.STUDENT)
    posting = create_test_internship(db, org, title="Frontend Intern")

    prof = StudentProfile(user_id=student.id, university="AAU", department="CS")
    db.add(prof)
    db.commit()

    app_resp = apply_to_internship(
        db,
        posting.id,
        student.id,
        ApplicationCreate(cover_letter="React TypeScript enthusiast."),
    )

    dec_payload = ApplicationDecision(
        status=ApplicationStatus.ACCEPTED,
        decision_message="Congratulations, we are thrilled to offer you the internship!",
    )
    decide_application(db, app_resp.id, dec_payload, org)

    notif = db.scalar(
        select(Notification).where(
            Notification.user_id == student.id,
            Notification.kind == NotificationKind.APPLICATION_DECISION,
        )
    )
    assert notif is not None
    assert "Application Accepted: Frontend Intern" in notif.title
    assert "thrilled to offer you" in notif.message
    assert notif.link_path == f"/applications/{app_resp.id}"

    # Org is not notified
    org_dec_notifs = list(
        db.scalars(
            select(Notification).where(
                Notification.user_id == org.id,
                Notification.kind == NotificationKind.APPLICATION_DECISION,
            )
        )
    )
    assert len(org_dec_notifs) == 0
