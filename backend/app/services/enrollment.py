"""Business logic and database operations for course enrollments and rosters."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.models.course import Course, CourseStatus
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from app.schemas.enrollment import (
    EnrolledStudentResponse,
    EnrollmentActionResponse,
    EnrollmentResponse,
)


def get_course_roster(
    db: Session,
    course_id: int,
    current_user: User,
) -> list[EnrolledStudentResponse]:
    """Retrieve enrolled students roster for course owner or platform admin."""
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course:
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    is_owner = course.instructor_id == current_user.id
    is_admin = current_user.role == UserRole.ADMIN

    if not (is_owner or is_admin):
        raise ForbiddenException(
            message="Only the course owner or admin can view student roster",
            code="FORBIDDEN",
        )

    stmt = (
        select(Enrollment.student_id, User.full_name, User.email, Enrollment.enrolled_at)
        .join(User, Enrollment.student_id == User.id)
        .where(Enrollment.course_id == course_id)
        .order_by(Enrollment.enrolled_at.asc())
    )
    rows = db.execute(stmt).all()

    return [
        EnrolledStudentResponse(
            student_id=student_id,
            name=full_name,
            email=email,
            enrolled_at=enrolled_at,
        )
        for student_id, full_name, email, enrolled_at in rows
    ]


def enroll_student(
    db: Session,
    course_id: int,
    student_id: int,
) -> EnrollmentResponse:
    """Enroll a student in a published course."""
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course or course.status != CourseStatus.PUBLISHED:
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    existing = db.scalar(
        select(Enrollment).where(
            Enrollment.course_id == course_id,
            Enrollment.student_id == student_id,
        )
    )
    if existing:
        raise ConflictException(
            message="Already enrolled in this course",
            code="ALREADY_ENROLLED",
        )

    enrollment = Enrollment(course_id=course_id, student_id=student_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return EnrollmentResponse(
        id=enrollment.id,
        course_id=enrollment.course_id,
        student_id=enrollment.student_id,
        enrolled_at=enrollment.enrolled_at,
        message="Enrolled successfully",
    )


def leave_course(
    db: Session,
    course_id: int,
    student_id: int,
) -> EnrollmentActionResponse:
    """Unenroll a student from a course."""
    course = db.scalar(select(Course).where(Course.id == course_id))
    if not course or course.status != CourseStatus.PUBLISHED:
        raise NotFoundException(message="Course not found", code="COURSE_NOT_FOUND")

    enrollment = db.scalar(
        select(Enrollment).where(
            Enrollment.course_id == course_id,
            Enrollment.student_id == student_id,
        )
    )
    if not enrollment:
        raise NotFoundException(
            message="You are not enrolled in this course",
            code="NOT_ENROLLED",
        )

    db.delete(enrollment)
    db.commit()

    return EnrollmentActionResponse(detail="Successfully unenrolled from course")
