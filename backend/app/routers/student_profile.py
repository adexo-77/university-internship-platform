"""Student profile API router handling current student profile retrieval and updates."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.student_profile import StudentProfile
from app.models.user import User, UserRole
from app.schemas.student_profile import StudentProfileResponse, StudentProfileUpdateRequest
from app.services.student_profile import StudentProfileService

router = APIRouter(prefix="/students", tags=["students"])
require_student = require_roles(UserRole.STUDENT)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=StudentProfileResponse,
    summary="Get current student profile",
)
def get_my_student_profile(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> StudentProfile:
    """Retrieve profile details for the authenticated student."""
    return StudentProfileService.get_profile(db=db, user=current_user)


@router.put(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=StudentProfileResponse,
    summary="Update current student profile",
)
def update_my_student_profile(
    request: StudentProfileUpdateRequest,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> StudentProfile:
    """Update profile details for the authenticated student."""
    return StudentProfileService.update_profile(
        db=db,
        user=current_user,
        update_data=request,
    )
