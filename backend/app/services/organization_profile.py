"""Domain service implementing organization profile retrieval and updates."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization_profile import OrganizationProfile
from app.models.user import User
from app.schemas.organization_profile import OrganizationProfileUpdateRequest


class OrganizationProfileService:
    """Organization profile business logic."""

    @staticmethod
    def get_profile(db: Session, user: User) -> OrganizationProfile:
        """Retrieve organization profile for the authenticated user, creating if missing."""
        profile = db.scalar(
            select(OrganizationProfile).where(OrganizationProfile.user_id == user.id)
        )
        if profile is None:
            profile = OrganizationProfile(
                user_id=user.id,
                organization_name=user.full_name,
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        return profile

    @staticmethod
    def update_profile(
        db: Session,
        user: User,
        update_data: OrganizationProfileUpdateRequest,
    ) -> OrganizationProfile:
        """Update organization profile details for the authenticated user."""
        profile = db.scalar(
            select(OrganizationProfile).where(OrganizationProfile.user_id == user.id)
        )
        if profile is None:
            profile = OrganizationProfile(
                user_id=user.id,
                organization_name=update_data.organization_name,
            )
            db.add(profile)

        profile.organization_name = update_data.organization_name
        profile.industry = update_data.industry
        profile.location = update_data.location
        profile.website = update_data.website
        profile.description = update_data.description

        db.commit()
        db.refresh(profile)
        return profile
