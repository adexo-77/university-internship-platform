"""Thin router for course assignment creation, listing, details, updates, and deletion."""

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.user import User, UserRole
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentResponse,
    AssignmentUpdate,
)
from app.services import assignment as assignment_service

router = APIRouter(tags=["assignments"])

require_instructor = require_roles(UserRole.INSTRUCTOR)


@router.post(
    "/courses/{id}/assignments",
    response_model=AssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new course assignment",
)
def create_course_assignment(
    payload: AssignmentCreate,
    id: int = Path(..., description="Course ID"),
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
) -> AssignmentResponse:
    """Create a new course assignment for the owner instructor."""
    return assignment_service.create_assignment(
        db=db,
        course_id=id,
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/courses/{id}/assignments",
    response_model=list[AssignmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List assignments for a course",
)
def list_course_assignments(
    id: int = Path(..., description="Course ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[AssignmentResponse]:
    """Retrieve all assignments for an authorized user (owner, admin, or enrolled student)."""
    return assignment_service.get_course_assignments(
        db=db,
        course_id=id,
        current_user=current_user,
    )


@router.get(
    "/assignments/{id}",
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get assignment details",
)
def get_assignment(
    id: int = Path(..., description="Assignment ID"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AssignmentResponse:
    """Get single assignment details with student submission state if student."""
    return assignment_service.get_assignment_by_id(
        db=db,
        assignment_id=id,
        current_user=current_user,
    )


@router.patch(
    "/assignments/{id}",
    response_model=AssignmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update assignment details",
)
def update_assignment(
    payload: AssignmentUpdate,
    id: int = Path(..., description="Assignment ID"),
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
) -> AssignmentResponse:
    """Update assignment fields and enforce max_points grade constraints."""
    return assignment_service.update_assignment(
        db=db,
        assignment_id=id,
        payload=payload,
        current_user=current_user,
    )


@router.delete(
    "/assignments/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an assignment",
)
def delete_assignment(
    id: int = Path(..., description="Assignment ID"),
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
) -> None:
    """Delete an assignment if no submissions have been made."""
    assignment_service.delete_assignment(
        db=db,
        assignment_id=id,
        current_user=current_user,
    )
