"""Thin router for assignment submissions, roster viewing, and grading."""

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.schemas.submission import (
    StudentSubmissionRosterItem,
    SubmissionGrade,
    SubmissionResponse,
    SubmissionSubmit,
)
from app.services import submission as submission_service

router = APIRouter(tags=["submissions"])

require_student = require_roles(UserRole.STUDENT)
require_instructor = require_roles(UserRole.INSTRUCTOR)
require_instructor_or_admin = require_roles(UserRole.INSTRUCTOR, UserRole.ADMIN)


@router.put(
    "/assignments/{id}/submission",
    response_model=SubmissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit or resubmit assignment work",
)
def submit_assignment(
    payload: SubmissionSubmit,
    id: int = Path(..., description="Assignment ID"),
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    """Submit work for an assignment (only enrolled students, 409 if graded)."""
    return submission_service.submit_assignment(
        db=db,
        assignment_id=id,
        payload=payload,
        current_user=current_user,
    )


@router.get(
    "/assignments/{id}/submission",
    response_model=SubmissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get student's own submission",
)
def get_own_submission(
    id: int = Path(..., description="Assignment ID"),
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    """Retrieve the authenticated student's own submission."""
    return submission_service.get_student_submission(
        db=db,
        assignment_id=id,
        current_user=current_user,
    )


@router.get(
    "/assignments/{id}/submissions",
    response_model=list[StudentSubmissionRosterItem],
    status_code=status.HTTP_200_OK,
    summary="List all enrolled students and submissions",
)
def list_assignment_submissions(
    id: int = Path(..., description="Assignment ID"),
    current_user: User = Depends(require_instructor_or_admin),
    db: Session = Depends(get_db),
) -> list[StudentSubmissionRosterItem]:
    """Retrieve every enrolled student and their submission (owner instructor or admin)."""
    return submission_service.get_assignment_submissions_roster(
        db=db,
        assignment_id=id,
        current_user=current_user,
    )


@router.put(
    "/submissions/{id}/grade",
    response_model=SubmissionResponse,
    status_code=status.HTTP_200_OK,
    summary="Grade a submission",
)
def grade_submission(
    payload: SubmissionGrade,
    id: int = Path(..., description="Submission ID"),
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db),
) -> SubmissionResponse:
    """Grade an assignment submission (owner instructor only, admin read-only)."""
    return submission_service.grade_submission(
        db=db,
        submission_id=id,
        payload=payload,
        current_user=current_user,
    )
