"""Business logic and database operations for course assignments."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.notification import NotificationKind
from app.models.submission import Submission
from app.models.user import User, UserRole
from app.schemas.assignment import AssignmentCreate, AssignmentResponse, AssignmentUpdate
from app.services.notification import create_notification


def check_course_access(db: Session, course: Course, user: User) -> bool:
    """Verify if user has permission to view course assignments."""
    if user.role == UserRole.ADMIN or course.instructor_id == user.id:
        return True
    if user.role == UserRole.STUDENT:
        enrolled = db.scalar(
            select(Enrollment.id).where(
                Enrollment.course_id == course.id,
                Enrollment.student_id == user.id,
            )
        )
        return enrolled is not None
    return False


def _attach_submission(resp: AssignmentResponse, sub: Submission | None) -> None:
    if sub:
        resp.submission_status = "graded" if sub.grade is not None else "submitted"
        resp.is_late = sub.is_late
        resp.grade = sub.grade
    else:
        resp.submission_status = "not_submitted"
        resp.is_late = None
        resp.grade = None


def create_assignment(
    db: Session,
    course_id: int,
    payload: AssignmentCreate,
    current_user: User,
) -> AssignmentResponse:
    """Create a new course assignment for the course owner instructor."""
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    if current_user.role != UserRole.INSTRUCTOR or course.instructor_id != current_user.id:
        raise ForbiddenException(
            message="Only the course instructor can create assignments",
            code="FORBIDDEN",
        )

    now = datetime.now(UTC)
    if payload.due_at <= now:
        raise ConflictException(
            message="Due date must be in the future on creation",
            code="INVALID_DUE_DATE",
        )

    assignment = Assignment(
        course_id=course_id,
        title=payload.title,
        description=payload.description,
        due_at=payload.due_at,
        max_points=payload.max_points,
    )
    db.add(assignment)
    db.flush()

    enrolled_ids = list(
        db.scalars(select(Enrollment.student_id).where(Enrollment.course_id == course_id))
    )
    for student_id in enrolled_ids:
        create_notification(
            db,
            user_id=student_id,
            actor_id=current_user.id,
            kind=NotificationKind.ASSIGNMENT_CREATED,
            title=f"New Assignment: {assignment.title}",
            message=f"A new assignment '{assignment.title}' was posted in '{course.title}'.",
            link_path=f"/assignments/{assignment.id}",
        )

    db.commit()
    db.refresh(assignment)
    resp = AssignmentResponse.model_validate(assignment)
    resp.course_title = course.title
    return resp


def get_course_assignments(
    db: Session,
    course_id: int,
    current_user: User,
) -> list[AssignmentResponse]:
    """Retrieve all assignments for a course with student status if applicable."""
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course or not check_course_access(db, course, current_user):
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    assignments = list(
        db.scalars(
            select(Assignment)
            .where(Assignment.course_id == course_id)
            .order_by(Assignment.due_at.asc())
        )
    )

    if not assignments:
        return []

    # Map student submissions if current user is a student
    submissions_map: dict[int, Submission] = {}
    if current_user.role == UserRole.STUDENT:
        assignment_ids = [a.id for a in assignments]
        sub_rows = db.scalars(
            select(Submission).where(
                Submission.assignment_id.in_(assignment_ids),
                Submission.student_id == current_user.id,
            )
        ).all()
        submissions_map = {s.assignment_id: s for s in sub_rows}

    responses: list[AssignmentResponse] = []
    for item in assignments:
        resp = AssignmentResponse.model_validate(item)
        resp.course_title = course.title
        if current_user.role == UserRole.STUDENT:
            _attach_submission(resp, submissions_map.get(item.id))
        responses.append(resp)

    return responses


def get_assignment_by_id(
    db: Session,
    assignment_id: int,
    current_user: User,
) -> AssignmentResponse:
    """Retrieve single assignment details with student submission state if student."""
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise NotFoundException(message="Assignment not found", code="ASSIGNMENT_NOT_FOUND")

    course = db.scalar(select(Course).where(Course.id == assignment.course_id))
    if not course or not check_course_access(db, course, current_user):
        raise NotFoundException(message="Assignment not found", code="ASSIGNMENT_NOT_FOUND")

    resp = AssignmentResponse.model_validate(assignment)
    resp.course_title = course.title
    if current_user.role == UserRole.STUDENT:
        sub = db.scalar(
            select(Submission).where(
                Submission.assignment_id == assignment_id,
                Submission.student_id == current_user.id,
            )
        )
        _attach_submission(resp, sub)

    return resp


def update_assignment(
    db: Session,
    assignment_id: int,
    payload: AssignmentUpdate,
    current_user: User,
) -> AssignmentResponse:
    """Update assignment fields and enforce max_points constraints against existing grades."""
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise NotFoundException(message="Assignment not found", code="ASSIGNMENT_NOT_FOUND")

    course = db.scalar(select(Course).where(Course.id == assignment.course_id))
    if not course or course.instructor_id != current_user.id:
        raise ForbiddenException(
            message="Only the course instructor can update assignments",
            code="FORBIDDEN",
        )

    if payload.max_points is not None:
        max_existing_grade = db.scalar(
            select(func.max(Submission.grade)).where(
                Submission.assignment_id == assignment_id,
                Submission.grade.is_not(None),
            )
        )
        if max_existing_grade is not None and payload.max_points < max_existing_grade:
            msg = f"max_points cannot drop below highest grade ({max_existing_grade})"
            raise ConflictException(
                message=msg,
                code="GRADE_BOUNDS_CONFLICT",
            )
        assignment.max_points = payload.max_points

    for field in ("title", "description", "due_at"):
        val = getattr(payload, field)
        if val is not None:
            setattr(assignment, field, val)

    db.commit()
    db.refresh(assignment)
    resp = AssignmentResponse.model_validate(assignment)
    resp.course_title = course.title
    return resp


def delete_assignment(
    db: Session,
    assignment_id: int,
    current_user: User,
) -> None:
    """Delete an assignment if no submissions have been made."""
    assignment = db.scalar(select(Assignment).where(Assignment.id == assignment_id))
    if not assignment:
        raise NotFoundException(message="Assignment not found", code="ASSIGNMENT_NOT_FOUND")

    course = db.scalar(select(Course).where(Course.id == assignment.course_id))
    if not course or course.instructor_id != current_user.id:
        raise ForbiddenException(
            message="Only the course instructor can delete assignments",
            code="FORBIDDEN",
        )

    submissions_count = db.scalar(
        select(func.count(Submission.id)).where(Submission.assignment_id == assignment_id)
    )
    if submissions_count and submissions_count > 0:
        raise ConflictException(
            message="Cannot delete an assignment with existing student submissions",
            code="SUBMISSIONS_EXIST",
        )

    db.delete(assignment)
    db.commit()
