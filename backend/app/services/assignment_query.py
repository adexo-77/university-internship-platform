"""Read and access query operations for course assignments."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.submission import Submission
from app.models.user import User, UserRole
from app.schemas.assignment import AssignmentResponse


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
