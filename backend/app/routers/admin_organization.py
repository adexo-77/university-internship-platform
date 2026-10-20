"""Admin organization approval API router."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.organization_profile import ApprovalStatus
from app.models.user import User, UserRole
from app.schemas.admin_organization import (
    AdminOrganizationApprovalRequest,
    AdminOrganizationItem,
    AdminOrganizationListResponse,
)
from app.services.admin_organization import AdminOrganizationService

router = APIRouter(prefix="/admin/organizations", tags=["admin-organizations"])
require_admin = require_roles(UserRole.ADMIN)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=AdminOrganizationListResponse,
    summary="List organizations for review",
)
def list_organizations(
    approval_status: ApprovalStatus | None = Query(
        default=None, description="Filter by approval status"
    ),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminOrganizationListResponse:
    """Retrieve paginated organization directory with approval status filter."""
    return AdminOrganizationService.list_organizations(
        db=db,
        approval_status=approval_status,
        limit=limit,
        offset=offset,
    )


@router.put(
    "/{user_id}/approval",
    status_code=status.HTTP_200_OK,
    response_model=AdminOrganizationItem,
    summary="Update organization approval status",
)
def update_organization_approval(
    user_id: int,
    payload: AdminOrganizationApprovalRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminOrganizationItem:
    """Approve, reject, or mark pending an organization with an optional review note."""
    return AdminOrganizationService.update_approval(
        db=db,
        user_id=user_id,
        payload=payload,
        current_admin=current_admin,
    )
