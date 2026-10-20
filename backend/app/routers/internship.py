"""Thin router for internship postings creation, listing, details, and updates."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.internship import InternshipWorkMode
from app.models.user import User, UserRole
from app.schemas.internship import (
    InternshipCreate,
    InternshipListResponse,
    InternshipResponse,
    InternshipUpdate,
)
from app.services import internship as internship_service
from app.services import internship_catalog as catalog_service

router = APIRouter(tags=["internships"])

require_organization = require_roles(UserRole.ORGANIZATION)


@router.post(
    "/internships",
    response_model=InternshipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new internship posting",
)
def create_internship(
    payload: InternshipCreate,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
) -> InternshipResponse:
    """Create a new internship posting in draft status owned by the authenticated organization."""
    return internship_service.create_internship(
        db=db,
        organization_id=current_user.id,
        payload=payload,
    )


@router.get(
    "/organizations/me/internships",
    response_model=list[InternshipResponse],
    status_code=status.HTTP_200_OK,
    summary="Get organization's own internship postings",
)
def get_my_internships(
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
) -> list[InternshipResponse]:
    """Retrieve all internship postings owned by authenticated organization."""
    return internship_service.get_organization_internships(
        db=db,
        organization_id=current_user.id,
    )


@router.patch(
    "/internships/{id}",
    response_model=InternshipResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an internship posting",
)
def update_internship(
    id: int,
    payload: InternshipUpdate,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
) -> InternshipResponse:
    """Update internship details or lifecycle status."""
    return internship_service.update_internship(
        db=db,
        internship_id=id,
        payload=payload,
        current_user=current_user,
    )


@router.post(
    "/internships/{id}/submit",
    response_model=InternshipResponse,
    status_code=status.HTTP_200_OK,
    summary="Submit an internship posting for admin review",
)
def submit_internship(
    id: int,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
) -> InternshipResponse:
    """Submit a draft or rejected internship posting for administrative review."""
    return internship_service.submit_internship(
        db=db,
        internship_id=id,
        current_user=current_user,
    )


@router.post(
    "/internships/{id}/withdraw",
    response_model=InternshipResponse,
    status_code=status.HTTP_200_OK,
    summary="Withdraw an internship posting to draft",
)
def withdraw_internship(
    id: int,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
) -> InternshipResponse:
    """Withdraw a pending_review internship posting back to draft status."""
    return internship_service.withdraw_internship(
        db=db,
        internship_id=id,
        current_user=current_user,
    )


@router.post(
    "/internships/{id}/close",
    response_model=InternshipResponse,
    status_code=status.HTTP_200_OK,
    summary="Close an open internship posting",
)
def close_internship(
    id: int,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
) -> InternshipResponse:
    """Close an active open internship posting."""
    return internship_service.close_internship(
        db=db,
        internship_id=id,
        current_user=current_user,
    )


@router.get(
    "/internships",
    response_model=InternshipListResponse,
    status_code=status.HTTP_200_OK,
    summary="Browse internship catalog",
)
def list_internships(
    q: str | None = Query(default=None, description="Search keyword for title or organization"),
    work_mode: InternshipWorkMode | None = Query(default=None, description="Filter by work mode"),
    limit: int = Query(default=20, ge=1, le=100, description="Page limit"),
    offset: int = Query(default=0, ge=0, description="Page offset"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InternshipListResponse:
    """List open internship postings for students or all postings for administrators."""
    return catalog_service.list_internships(
        db=db,
        current_user=current_user,
        q=q,
        work_mode=work_mode,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/internships/{id}",
    response_model=InternshipResponse,
    status_code=status.HTTP_200_OK,
    summary="Get internship posting by ID",
)
def get_internship_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> InternshipResponse:
    """Retrieve detailed information for an internship posting."""
    return catalog_service.get_internship_by_id(
        db=db,
        internship_id=id,
        current_user=current_user,
    )
