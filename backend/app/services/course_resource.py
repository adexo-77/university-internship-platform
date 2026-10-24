"""Business logic and database operations for course learning resources."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.course import Course, CourseStatus
from app.models.course_resource import CourseResource
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from app.schemas.course_resource import (
    CourseResourceCreate,
    CourseResourceResponse,
    CourseResourceUpdate,
)

MAX_RESOURCES_PER_COURSE = 50


def get_course_resources(
    db: Session,
    course_id: int,
    current_user: User,
) -> list[CourseResourceResponse]:
    """Retrieve resources for owner instructor, admin, or enrolled student on published course."""
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    is_owner = current_user.role == UserRole.INSTRUCTOR and course.instructor_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if not (is_owner or is_admin):
        if current_user.role != UserRole.STUDENT or course.status == CourseStatus.DRAFT:
            raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

        enrolled = db.scalar(
            select(Enrollment.id).where(
                Enrollment.course_id == course_id,
                Enrollment.student_id == current_user.id,
            )
        )
        if not enrolled:
            raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    stmt = (
        select(CourseResource)
        .where(CourseResource.course_id == course_id)
        .order_by(CourseResource.created_at.asc(), CourseResource.id.asc())
    )
    items = list(db.scalars(stmt))
    return [CourseResourceResponse.model_validate(r) for r in items]


def create_course_resource(
    db: Session,
    course_id: int,
    payload: CourseResourceCreate,
    current_user: User,
) -> CourseResourceResponse:
    """Create a new course learning resource for the owner instructor."""
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    if current_user.role != UserRole.INSTRUCTOR or course.instructor_id != current_user.id:
        raise ForbiddenException(
            message="Only the course instructor can create resources",
            code="FORBIDDEN",
        )

    count = (
        db.scalar(
            select(func.count(CourseResource.id)).where(CourseResource.course_id == course_id)
        )
        or 0
    )
    if count >= MAX_RESOURCES_PER_COURSE:
        raise ConflictException(
            message=f"Course cannot have more than {MAX_RESOURCES_PER_COURSE} resources",
            code="RESOURCE_LIMIT_EXCEEDED",
        )

    resource = CourseResource(
        course_id=course_id,
        title=payload.title,
        url=payload.url,
        description=payload.description,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return CourseResourceResponse.model_validate(resource)


def update_course_resource(
    db: Session,
    resource_id: int,
    payload: CourseResourceUpdate,
    current_user: User,
) -> CourseResourceResponse:
    """Update title, url, or description of a course resource for owner instructor."""
    resource = db.scalar(select(CourseResource).where(CourseResource.id == resource_id))
    if not resource:
        raise NotFoundException(message="Resource not found", code="RESOURCE_NOT_FOUND")

    course = db.scalar(select(Course).where(Course.id == resource.course_id))
    if (
        not course
        or current_user.role != UserRole.INSTRUCTOR
        or course.instructor_id != current_user.id
    ):
        raise ForbiddenException(
            message="Only the course instructor can update resources",
            code="FORBIDDEN",
        )

    update_data = payload.model_dump(exclude_unset=True)
    if "title" in update_data:
        resource.title = update_data["title"]
    if "url" in update_data:
        resource.url = update_data["url"]
    if "description" in update_data:
        resource.description = update_data["description"]

    db.commit()
    db.refresh(resource)
    return CourseResourceResponse.model_validate(resource)


def delete_course_resource(
    db: Session,
    resource_id: int,
    current_user: User,
) -> None:
    """Delete a course resource for owner instructor."""
    resource = db.scalar(select(CourseResource).where(CourseResource.id == resource_id))
    if not resource:
        raise NotFoundException(message="Resource not found", code="RESOURCE_NOT_FOUND")

    course = db.scalar(select(Course).where(Course.id == resource.course_id))
    if (
        not course
        or current_user.role != UserRole.INSTRUCTOR
        or course.instructor_id != current_user.id
    ):
        raise ForbiddenException(
            message="Only the course instructor can delete resources",
            code="FORBIDDEN",
        )

    db.delete(resource)
    db.commit()
