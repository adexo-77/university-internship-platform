"""Business logic and database operations for course creation and updates."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.course import (
    CourseCreate,
    CourseResponse,
    CourseUpdate,
)


def create_course(db: Session, instructor_id: int, payload: CourseCreate) -> CourseResponse:
    """Create a new course owned by the authenticated instructor."""
    course = Course(
        instructor_id=instructor_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    instructor_name = db.scalar(select(User.full_name).where(User.id == instructor_id))
    return CourseResponse(
        id=course.id,
        instructor_id=course.instructor_id,
        instructor_name=instructor_name,
        title=course.title,
        description=course.description,
        status=course.status,
        created_at=course.created_at,
        updated_at=course.updated_at,
        enrolled=False,
        enrolled_count=0,
    )


def update_course(
    db: Session,
    course_id: int,
    payload: CourseUpdate,
    current_user: User,
) -> CourseResponse:
    """Update title, description, or publish status of a course."""
    row = db.execute(
        select(Course, User.full_name)
        .join(User, Course.instructor_id == User.id)
        .where(Course.id == course_id)
    ).first()

    if not row:
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    course, instructor_name = row

    is_owner = course.instructor_id == current_user.id
    is_admin = current_user.role.value == "admin"

    if not (is_owner or is_admin):
        raise ForbiddenException(
            message="Only the course owner or an admin can update this course",
            code="FORBIDDEN",
        )

    if course.status == CourseStatus.PUBLISHED and payload.status == CourseStatus.DRAFT:
        raise ConflictException(
            message="Published courses cannot be reverted to draft",
            code="INVALID_STATUS_TRANSITION",
        )

    if payload.title is not None:
        course.title = payload.title
    if payload.description is not None:
        course.description = payload.description
    if payload.status is not None:
        course.status = payload.status

    db.commit()
    db.refresh(course)

    enrolled_count = (
        db.scalar(select(func.count(Enrollment.id)).where(Enrollment.course_id == course.id)) or 0
    )

    return CourseResponse(
        id=course.id,
        instructor_id=course.instructor_id,
        instructor_name=instructor_name,
        title=course.title,
        description=course.description,
        status=course.status,
        created_at=course.created_at,
        updated_at=course.updated_at,
        enrolled_count=enrolled_count,
    )
