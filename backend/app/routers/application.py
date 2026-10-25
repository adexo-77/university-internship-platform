"""Thin router for internship applications, decisions, and status transitions."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, require_roles
from app.models.application import ApplicationStatus
from app.models.user import User, UserRole
from app.schemas.application import (
    ApplicationCreate,
    ApplicationDecision,
    ApplicationResponse,
)
from app.services import application as application_service

router = APIRouter(tags=["applications"])

require_student = require_roles(UserRole.STUDENT)
require_organization = require_roles(UserRole.ORGANIZATION)
require_org_admin_or_coordinator = require_roles(
    UserRole.ORGANIZATION, UserRole.ADMIN, UserRole.COORDINATOR
)


@router.post(
    "/internships/{id}/applications",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an application to an internship posting",
)
def apply_to_internship(
    id: int,
    payload: ApplicationCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    """Submit an application as the authenticated student to an open internship posting."""
    return application_service.apply_to_internship(
        db=db,
        posting_id=id,
        student_id=current_user.id,
        payload=payload,
    )


@router.get(
    "/internships/{id}/applications",
    response_model=list[ApplicationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get applicant roster for an internship posting",
)
def get_internship_applications(
    id: int,
    status_filter: ApplicationStatus | None = Query(
        default=None, alias="status", description="Filter applicants by status"
    ),
    current_user: User = Depends(require_org_admin_or_coordinator),
    db: Session = Depends(get_db),
) -> list[ApplicationResponse]:
    """Retrieve applicant roster with profile details for owner or admin."""
    return application_service.get_internship_applications(
        db=db,
        posting_id=id,
        current_user=current_user,
        status=status_filter,
    )


@router.get(
    "/students/me/applications",
    response_model=list[ApplicationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get student's own applications",
)
def get_my_applications(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> list[ApplicationResponse]:
    """Retrieve all applications submitted by the authenticated student."""
    return application_service.get_student_applications(
        db=db,
        student_id=current_user.id,
    )


@router.post(
    "/applications/{id}/withdraw",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Withdraw a submitted or shortlisted application",
)
def withdraw_application(
    id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    """Withdraw an application submitted by the student while pending decision."""
    return application_service.withdraw_application(
        db=db,
        application_id=id,
        student_id=current_user.id,
    )


@router.get(
    "/applications/{id}",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get application detail by ID",
)
def get_application_by_id(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    """Retrieve application detail for the student owner, posting organization, or admin."""
    return application_service.get_application_by_id(
        db=db,
        application_id=id,
        current_user=current_user,
    )


@router.put(
    "/applications/{id}/decision",
    response_model=ApplicationResponse,
    status_code=status.HTTP_200_OK,
    summary="Record decision on an application",
)
def decide_application(
    id: int,
    payload: ApplicationDecision,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
) -> ApplicationResponse:
    """Record an organization decision (shortlisted, accepted, or rejected)."""
    return application_service.decide_application(
        db=db,
        application_id=id,
        payload=payload,
        current_user=current_user,
    )
