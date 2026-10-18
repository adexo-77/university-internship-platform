"""Organization profile API router handling organization profile retrieval and updates."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.organization_profile import OrganizationProfile
from app.models.user import User, UserRole
from app.schemas.organization_profile import (
    OrganizationProfileResponse,
    OrganizationProfileUpdateRequest,
)
from app.services.organization_profile import OrganizationProfileService

router = APIRouter(prefix="/organizations", tags=["organizations"])
require_organization = require_roles(UserRole.ORGANIZATION)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationProfileResponse,
    summary="Get current organization profile",
)
def get_my_organization_profile(
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
) -> OrganizationProfile:
    """Retrieve profile details for the authenticated organization."""
    return OrganizationProfileService.get_profile(db=db, user=current_user)


@router.put(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=OrganizationProfileResponse,
    summary="Update current organization profile",
)
def update_my_organization_profile(
    request: OrganizationProfileUpdateRequest,
    current_user: User = Depends(require_organization),
    db: Session = Depends(get_db),
) -> OrganizationProfile:
    """Update profile details for the authenticated organization."""
    return OrganizationProfileService.update_profile(
        db=db,
        user=current_user,
        update_data=request,
    )
