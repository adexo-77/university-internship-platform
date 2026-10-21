from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.internship import InternshipStatus
from app.models.user import User, UserRole
from app.schemas.admin_internship import InternshipReviewRequest
from app.schemas.internship import InternshipListResponse, InternshipResponse
from app.services import admin_internship as admin_internship_service

router = APIRouter(prefix="/admin/internships", tags=["admin-internships"])

require_admin = require_roles(UserRole.ADMIN)

ReviewStatusParam = Literal[
    "all",
    InternshipStatus.PENDING_REVIEW,
    InternshipStatus.OPEN,
    InternshipStatus.REJECTED,
    InternshipStatus.CLOSED,
    InternshipStatus.DRAFT,
]


@router.get(
    "",
    response_model=InternshipListResponse,
    status_code=status.HTTP_200_OK,
    summary="List internship postings for admin review",
)
def list_admin_internships(
    review_status: ReviewStatusParam | None = Query(
        default=None,
        alias="status",
        description="Filter by posting status (defaults to pending_review, or 'all')",
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
    _current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> InternshipListResponse:
    """Retrieve internship postings in review queue, ordered oldest first."""
    return admin_internship_service.list_admin_internships(
        db=db,
        status=review_status,
        limit=limit,
        offset=offset,
    )


@router.put(
    "/{id}/review",
    response_model=InternshipResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve, reject, or take down an internship posting",
)
def review_internship(
    id: int,
    payload: InternshipReviewRequest,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> InternshipResponse:
    """Review an internship posting by approving or rejecting, or taking down an open posting."""
    return admin_internship_service.review_internship(
        db=db,
        internship_id=id,
        reviewer_id=current_user.id,
        payload=payload,
    )
