"""Study plan router providing student-specific deterministic study scheduling."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.schemas.study_plan import StudyPlanResponse
from app.services.study_plan import (
    DEFAULT_PLAN_DAYS,
    MAX_PLAN_DAYS,
    MAX_UTC_OFFSET_MINUTES,
    MIN_PLAN_DAYS,
    MIN_UTC_OFFSET_MINUTES,
    generate_study_plan,
)

router = APIRouter(prefix="/students", tags=["students"])
require_student = require_roles(UserRole.STUDENT)


@router.get(
    "/me/study-plan",
    status_code=status.HTTP_200_OK,
    response_model=StudyPlanResponse,
    summary="Get rule-based study plan and weekly progress summary",
)
def get_student_study_plan(
    days: int = Query(
        default=DEFAULT_PLAN_DAYS,
        ge=MIN_PLAN_DAYS,
        le=MAX_PLAN_DAYS,
        description="Number of days in study plan window (3 to 14)",
    ),
    utc_offset_minutes: int = Query(
        default=0,
        ge=MIN_UTC_OFFSET_MINUTES,
        le=MAX_UTC_OFFSET_MINUTES,
        description="Client timezone offset from UTC in minutes (from -720 to 840)",
    ),
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> StudyPlanResponse:
    """Generate a deterministic rule-based study plan for the signed-in student."""
    return generate_study_plan(
        db=db,
        student=current_user,
        days=days,
        utc_offset_minutes=utc_offset_minutes,
    )
