"""Business logic and database operations for course domain."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from app.schemas.course import (
    CourseCreate,
    CourseListResponse,
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


def list_courses(
    db: Session,
    current_user: User,
    q: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> CourseListResponse:
    """List courses with title search and pagination based on user role."""
    clamped_limit = min(max(limit, 1), 100)
    clamped_offset = max(offset, 0)

    stmt = select(Course, User.full_name).join(User, Course.instructor_id == User.id)
    count_stmt = select(func.count(Course.id))

    if current_user.role != UserRole.ADMIN:
        stmt = stmt.where(Course.status == CourseStatus.PUBLISHED)
        count_stmt = count_stmt.where(Course.status == CourseStatus.PUBLISHED)

    if q and q.strip():
        search_filter = Course.title.ilike(f"%{q.strip()}%")
        stmt = stmt.where(search_filter)
        count_stmt = count_stmt.where(search_filter)

    total = db.scalar(count_stmt) or 0

    stmt = stmt.order_by(Course.created_at.desc()).offset(clamped_offset).limit(clamped_limit)
    rows = db.execute(stmt).all()

    enrolled_set: set[int] = set()
    if current_user.role == UserRole.STUDENT and rows:
        course_ids = [c.id for c, _ in rows]
        enrolled_query = select(Enrollment.course_id).where(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id.in_(course_ids),
        )
        enrolled_set = set(db.scalars(enrolled_query).all())

    items = [
        CourseResponse(
            id=course.id,
            instructor_id=course.instructor_id,
            instructor_name=full_name,
            title=course.title,
            description=course.description,
            status=course.status,
            created_at=course.created_at,
            updated_at=course.updated_at,
            enrolled=(course.id in enrolled_set) if current_user.role == UserRole.STUDENT else None,
        )
        for course, full_name in rows
    ]

    return CourseListResponse(
        items=items,
        total=total,
        limit=clamped_limit,
        offset=clamped_offset,
    )


def get_course_by_id(db: Session, course_id: int, current_user: User) -> CourseResponse:
    """Retrieve course details if visible to the user, otherwise 404."""
    row = db.execute(
        select(Course, User.full_name)
        .join(User, Course.instructor_id == User.id)
        .where(Course.id == course_id)
    ).first()

    if not row:
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    course, instructor_name = row

    is_owner = course.instructor_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN
    is_published = course.status == CourseStatus.PUBLISHED

    if not (is_published or is_owner or is_admin):
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    enrolled: bool | None = None
    if current_user.role == UserRole.STUDENT:
        enrolled_query = select(Enrollment.id).where(
            Enrollment.course_id == course.id,
            Enrollment.student_id == current_user.id,
        )
        enrolled = db.scalar(enrolled_query) is not None

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
        enrolled=enrolled,
        enrolled_count=enrolled_count,
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
    is_admin = current_user.role == UserRole.ADMIN

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


def get_instructor_courses(db: Session, instructor_id: int) -> list[CourseResponse]:
    """Retrieve instructor's courses with enrolled student counts."""
    instructor_name = db.scalar(select(User.full_name).where(User.id == instructor_id))

    stmt = (
        select(Course, func.count(Enrollment.id).label("enrolled_count"))
        .outerjoin(Enrollment, Course.id == Enrollment.course_id)
        .where(Course.instructor_id == instructor_id)
        .group_by(Course.id)
        .order_by(Course.created_at.desc())
    )
    rows = db.execute(stmt).all()

    return [
        CourseResponse(
            id=course.id,
            instructor_id=course.instructor_id,
            instructor_name=instructor_name,
            title=course.title,
            description=course.description,
            status=course.status,
            created_at=course.created_at,
            updated_at=course.updated_at,
            enrolled=False,
            enrolled_count=count,
        )
        for course, count in rows
    ]


def get_student_courses(db: Session, student_id: int) -> list[CourseResponse]:
    """Retrieve courses in which the student is currently enrolled."""
    stmt = (
        select(Course, User.full_name)
        .join(Enrollment, Course.id == Enrollment.course_id)
        .join(User, Course.instructor_id == User.id)
        .where(Enrollment.student_id == student_id)
        .order_by(Enrollment.enrolled_at.desc())
    )
    rows = db.execute(stmt).all()

    return [
        CourseResponse(
            id=course.id,
            instructor_id=course.instructor_id,
            instructor_name=instructor_name,
            title=course.title,
            description=course.description,
            status=course.status,
            created_at=course.created_at,
            updated_at=course.updated_at,
            enrolled=True,
        )
        for course, instructor_name in rows
    ]
