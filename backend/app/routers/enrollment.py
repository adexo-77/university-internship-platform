"""Thin router for course enrollment, unenrollment, and roster views."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.schemas.enrollment import (
    EnrolledStudentResponse,
    EnrollmentActionResponse,
    EnrollmentResponse,
)
from app.services import enrollment as enrollment_service

router = APIRouter(tags=["enrollments"])

require_student = require_roles(UserRole.STUDENT)
require_instructor_or_admin = require_roles(UserRole.INSTRUCTOR, UserRole.ADMIN)


@router.get(
    "/courses/{id}/students",
    response_model=list[EnrolledStudentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get enrolled student roster",
)
def get_course_students(
    id: int,
    current_user: User = Depends(require_instructor_or_admin),
    db: Session = Depends(get_db),
) -> list[EnrolledStudentResponse]:
    """Retrieve enrolled student roster for the course owner or admin."""
    return enrollment_service.get_course_roster(
        db=db,
        course_id=id,
        current_user=current_user,
    )


@router.post(
    "/courses/{id}/enrollment",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Enroll in course",
)
def enroll_course(
    id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> EnrollmentResponse:
    """Enroll the authenticated student in a published course."""
    return enrollment_service.enroll_student(
        db=db,
        course_id=id,
        student_id=current_user.id,
    )


@router.delete(
    "/courses/{id}/enrollment",
    response_model=EnrollmentActionResponse,
    status_code=status.HTTP_200_OK,
    summary="Leave course",
)
def leave_course(
    id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> EnrollmentActionResponse:
    """Unenroll the authenticated student from a course."""
    return enrollment_service.leave_course(
        db=db,
        course_id=id,
        student_id=current_user.id,
    )
