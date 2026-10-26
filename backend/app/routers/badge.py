"""API router for student achievement badges."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.schemas.badge import BadgeResponse
from app.services import badge as badge_service

router = APIRouter(tags=["badges"])
require_student = require_roles(UserRole.STUDENT)


@router.get(
    "/students/me/badges",
    response_model=list[BadgeResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current student achievement badges",
)
def get_my_badges(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> list[BadgeResponse]:
    """Retrieve computed achievement badges for the authenticated student."""
    return badge_service.get_student_badges(db=db, student=current_user)
