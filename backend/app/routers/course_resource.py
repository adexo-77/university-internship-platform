"""Thin router for course learning resource creation, listing, updates, and deletion."""

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.course_resource import (
    CourseResourceCreate,
    CourseResourceResponse,
    CourseResourceUpdate,
)
from app.services import course_resource as resource_service

router = APIRouter(tags=["course-resources"])

require_instructor = require_roles(UserRole.INSTRUCTOR)


@router.get(
    "/courses/{id}/resources",
    response_model=list[CourseResourceResponse],
    status_code=status.HTTP_200_OK,
    summary="List course resources",
)
def list_course_resources(
    id: int = Path(..., description="Course ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[CourseResourceResponse]:
    """Retrieve resources for owner instructor, admin, or enrolled student on published course."""
    return resource_service.get_course_resources(
        db=db,
        course_id=id,
        current_user=current_user,
    )


@router.post(
    "/courses/{id}/resources",
    response_model=CourseResourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a course resource",
)
def create_course_resource(
    payload: CourseResourceCreate,
    id: int = Path(..., description="Course ID"),
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
) -> CourseResourceResponse:
    """Create a new course learning resource for the course owner instructor."""
    return resource_service.create_course_resource(
        db=db,
        course_id=id,
        payload=payload,
        current_user=current_user,
    )


@router.patch(
    "/resources/{id}",
    response_model=CourseResourceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a course resource",
)
def update_course_resource(
    payload: CourseResourceUpdate,
    id: int = Path(..., description="Resource ID"),
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
) -> CourseResourceResponse:
    """Update title, url, or description of a course resource for owner instructor."""
    return resource_service.update_course_resource(
        db=db,
        resource_id=id,
        payload=payload,
        current_user=current_user,
    )


@router.delete(
    "/resources/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a course resource",
)
def delete_course_resource(
    id: int = Path(..., description="Resource ID"),
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
) -> None:
    """Delete a course resource for owner instructor."""
    resource_service.delete_course_resource(
        db=db,
        resource_id=id,
        current_user=current_user,
    )
