"""Business logic and database operations for assignment submissions and grading."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.notification import NotificationKind
from app.models.submission import Submission
from app.models.user import User, UserRole
from app.schemas.submission import (
    StudentSubmissionRosterItem,
    SubmissionGrade,
    SubmissionResponse,
    SubmissionSubmit,
)
from app.services.notification import create_notification


def _ensure_enrolled_student(db: Session, course_id: int, user: User) -> None:
    """Verify that user is a student currently enrolled in the course."""
    if user.role != UserRole.STUDENT:
        raise ForbiddenException(
            message="Only students can submit assignment work",
            code="FORBIDDEN",
        )
    is_enrolled = db.scalar(
        select(Enrollment.id).where(
            Enrollment.course_id == course_id,
            Enrollment.student_id == user.id,
        )
    )
    if not is_enrolled:
        raise NotFoundException(
            message="Assignment not found or not enrolled",
            code="NOT_FOUND",
        )


def submit_assignment(
    db: Session,
    assignment_id: int,
    payload: SubmissionSubmit,
    current_user: User,
    current_time: datetime | None = None,
) -> SubmissionResponse:
    """Create or update a student's submission for an assignment."""
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise NotFoundException(message="Assignment not found", code="ASSIGNMENT_NOT_FOUND")

    _ensure_enrolled_student(db, assignment.course_id, current_user)

    submission = db.scalar(
        select(Submission).where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == current_user.id,
        )
    )

    if submission and submission.graded_at is not None:
        raise ConflictException(
            message="Cannot update a submission that has already been graded",
            code="SUBMISSION_ALREADY_GRADED",
        )

    now = current_time or datetime.now(UTC)
    is_late = now > assignment.due_at

    if submission:
        submission.content = payload.content
        submission.link_url = payload.link_url
        submission.is_late = is_late
        submission.updated_at = now
    else:
        submission = Submission(
            assignment_id=assignment_id,
            student_id=current_user.id,
            content=payload.content,
            link_url=payload.link_url,
            is_late=is_late,
            submitted_at=now,
            updated_at=now,
        )
        db.add(submission)
        course = db.scalar(select(Course).where(Course.id == assignment.course_id))
        if course:
            create_notification(
                db,
                user_id=course.instructor_id,
                actor_id=current_user.id,
                kind=NotificationKind.FIRST_SUBMISSION,
                title=f"Submission: {assignment.title}",
                message=f"{current_user.full_name} submitted to '{assignment.title}'.",
                link_path=f"/assignments/{assignment.id}",
            )

    db.commit()
    db.refresh(submission)
    return SubmissionResponse.model_validate(submission)


def get_student_submission(
    db: Session,
    assignment_id: int,
    current_user: User,
) -> SubmissionResponse:
    """Retrieve the student's own submission for an assignment."""
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise NotFoundException(message="Assignment not found", code="ASSIGNMENT_NOT_FOUND")

    _ensure_enrolled_student(db, assignment.course_id, current_user)

    submission = db.scalar(
        select(Submission).where(
            Submission.assignment_id == assignment_id,
            Submission.student_id == current_user.id,
        )
    )
    if not submission:
        raise NotFoundException(
            message="No submission found for this assignment",
            code="SUBMISSION_NOT_FOUND",
        )

    return SubmissionResponse.model_validate(submission)


def get_assignment_submissions_roster(
    db: Session,
    assignment_id: int,
    current_user: User,
) -> list[StudentSubmissionRosterItem]:
    """Retrieve every enrolled student and their submission for owner instructor or admin."""
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise NotFoundException(message="Assignment not found", code="ASSIGNMENT_NOT_FOUND")

    course = db.scalar(select(Course).where(Course.id == assignment.course_id))
    if not course:
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    is_owner = course.instructor_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if not (is_owner or is_admin):
        raise NotFoundException(
            message="Assignment not found or unauthorized",
            code="NOT_FOUND",
        )

    # Fetch all students enrolled in this course
    enrolled_students = db.execute(
        select(User.id, User.full_name, User.email)
        .join(Enrollment, Enrollment.student_id == User.id)
        .where(Enrollment.course_id == course.id)
        .order_by(User.full_name.asc(), User.id.asc())
    ).all()

    # Fetch all submissions for this assignment
    submissions = db.scalars(
        select(Submission).where(Submission.assignment_id == assignment_id)
    ).all()
    sub_map = {s.student_id: s for s in submissions}

    roster: list[StudentSubmissionRosterItem] = []
    for s_id, s_name, s_email in enrolled_students:
        sub = sub_map.get(s_id)
        roster.append(
            StudentSubmissionRosterItem(
                student_id=s_id,
                student_name=s_name,
                student_email=s_email,
                submission=SubmissionResponse.model_validate(sub) if sub else None,
            )
        )

    return roster


def grade_submission(
    db: Session,
    submission_id: int,
    payload: SubmissionGrade,
    current_user: User,
) -> SubmissionResponse:
    """Grade an assignment submission for the owner instructor."""
    submission = db.scalar(select(Submission).where(Submission.id == submission_id))
    if not submission:
        raise NotFoundException(message="Submission not found", code="SUBMISSION_NOT_FOUND")

    assignment = db.scalar(select(Assignment).where(Assignment.id == submission.assignment_id))
    if not assignment:
        raise NotFoundException(message="Assignment not found", code="ASSIGNMENT_NOT_FOUND")

    course = db.scalar(select(Course).where(Course.id == assignment.course_id))
    if not course or course.instructor_id != current_user.id:
        raise ForbiddenException(
            message="Only the course instructor can grade submissions",
            code="FORBIDDEN",
        )

    if payload.grade < 0 or payload.grade > assignment.max_points:
        raise ConflictException(
            message=f"Grade must be between 0 and assignment max_points ({assignment.max_points})",
            code="GRADE_OUT_OF_BOUNDS",
        )

    now = datetime.now(UTC)
    submission.grade = payload.grade
    submission.feedback = payload.feedback
    submission.graded_at = now
    submission.graded_by = current_user.id

    create_notification(
        db,
        user_id=submission.student_id,
        actor_id=current_user.id,
        kind=NotificationKind.SUBMISSION_GRADED,
        title=f"Submission Graded: {assignment.title}",
        message=(
            f"Your submission for '{assignment.title}' was graded: "
            f"{payload.grade}/{assignment.max_points}."
        ),
        link_path=f"/assignments/{assignment.id}",
    )

    db.commit()
    db.refresh(submission)
    return SubmissionResponse.model_validate(submission)
