"""Thin router for course creation, listing, details, and updates."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.course import (
    CourseCreate,
    CourseListResponse,
    CourseResponse,
    CourseUpdate,
)
from app.services import course as course_service
from app.services import course_catalog as course_catalog_service

router = APIRouter(tags=["courses"])

require_instructor = require_roles(UserRole.INSTRUCTOR)
require_student = require_roles(UserRole.STUDENT)
require_instructor_or_admin = require_roles(UserRole.INSTRUCTOR, UserRole.ADMIN)


@router.post(
    "/courses",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new course",
)
def create_course(
    payload: CourseCreate,
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
) -> CourseResponse:
    """Create a course owned by the authenticated instructor."""
    return course_service.create_course(
        db=db,
        instructor_id=current_user.id,
        payload=payload,
    )


@router.get(
    "/courses",
    response_model=CourseListResponse,
    status_code=status.HTTP_200_OK,
    summary="List courses with search and pagination",
)
def list_courses(
    q: str | None = Query(default=None, description="Title search substring"),
    limit: int = Query(default=20, ge=1, le=100, description="Items limit"),
    offset: int = Query(default=0, ge=0, description="Items offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseListResponse:
    """List published courses (or all statuses for admin) with title search."""
    return course_catalog_service.list_courses(
        db=db,
        current_user=current_user,
        q=q,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/instructors/me/courses",
    response_model=list[CourseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get instructor's own courses",
)
def get_my_instructor_courses(
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
) -> list[CourseResponse]:
    """Retrieve all courses owned by the authenticated instructor with student counts."""
    return course_catalog_service.get_instructor_courses(
        db=db,
        instructor_id=current_user.id,
    )


@router.get(
    "/students/me/courses",
    response_model=list[CourseResponse],
    status_code=status.HTTP_200_OK,
    summary="Get student's enrolled courses",
)
def get_my_student_courses(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> list[CourseResponse]:
    """Retrieve all courses currently enrolled by the authenticated student."""
    return course_catalog_service.get_student_courses(
        db=db,
        student_id=current_user.id,
    )


@router.get(
    "/courses/{id}",
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Get course by ID",
)
def get_course_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseResponse:
    """Retrieve course details if published, owned by user, or requested by admin."""
    return course_catalog_service.get_course_by_id(
        db=db,
        course_id=id,
        current_user=current_user,
    )


@router.patch(
    "/courses/{id}",
    response_model=CourseResponse,
    status_code=status.HTTP_200_OK,
    summary="Update course",
)
def update_course(
    id: int,
    payload: CourseUpdate,
    current_user: User = Depends(require_instructor_or_admin),
    db: Session = Depends(get_db),
) -> CourseResponse:
    """Update title, description, or transition status from draft to published."""
    return course_service.update_course(
        db=db,
        course_id=id,
        payload=payload,
        current_user=current_user,
    )
