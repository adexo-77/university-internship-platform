"""Domain service implementing organization approval management by administrators."""

from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.user import User, UserRole
from app.schemas.admin_organization import (
    AdminOrganizationApprovalRequest,
    AdminOrganizationItem,
    AdminOrganizationListResponse,
)


class AdminOrganizationService:
    """Administrator organization approval business logic."""

    @staticmethod
    def list_organizations(
        db: Session,
        approval_status: ApprovalStatus | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> AdminOrganizationListResponse:
        """List organization profiles with approval status filter and pagination."""
        clamped_limit = min(max(limit, 1), 100)
        clamped_offset = max(offset, 0)

        stmt = (
            select(OrganizationProfile, User)
            .join(User, OrganizationProfile.user_id == User.id)
            .where(User.role == UserRole.ORGANIZATION)
        )
        count_stmt = (
            select(func.count(OrganizationProfile.id))
            .join(User, OrganizationProfile.user_id == User.id)
            .where(User.role == UserRole.ORGANIZATION)
        )

        if approval_status is not None:
            stmt = stmt.where(OrganizationProfile.approval_status == approval_status)
            count_stmt = count_stmt.where(OrganizationProfile.approval_status == approval_status)

        total = db.scalar(count_stmt) or 0
        rows = db.execute(
            stmt.order_by(OrganizationProfile.updated_at.desc())
            .offset(clamped_offset)
            .limit(clamped_limit)
        ).all()

        items = [
            AdminOrganizationItem(
                user_id=org.user_id,
                organization_name=org.organization_name,
                contact_name=user.full_name,
                email=user.email,
                industry=org.industry,
                location=org.location,
                approval_status=org.approval_status,
                approval_note=org.approval_note,
                reviewed_at=org.reviewed_at,
                reviewed_by=org.reviewed_by,
            )
            for org, user in rows
        ]

        return AdminOrganizationListResponse(
            items=items,
            total=total,
            limit=clamped_limit,
            offset=clamped_offset,
        )

    @staticmethod
    def update_approval(
        db: Session,
        user_id: int,
        payload: AdminOrganizationApprovalRequest,
        current_admin: User,
    ) -> AdminOrganizationItem:
        """Approve, reject, or mark pending an organization profile."""
        stmt = (
            select(OrganizationProfile, User)
            .join(User, OrganizationProfile.user_id == User.id)
            .where(OrganizationProfile.user_id == user_id)
        )
        row = db.execute(stmt).first()
        if row is None:
            raise NotFoundException(
                message="Organization profile not found",
                code="ORGANIZATION_NOT_FOUND",
            )

        org, user = row
        org.approval_status = payload.approval_status
        org.approval_note = payload.approval_note
        org.reviewed_at = datetime.now(UTC)
        org.reviewed_by = current_admin.id

        db.commit()
        db.refresh(org)

        return AdminOrganizationItem(
            user_id=org.user_id,
            organization_name=org.organization_name,
            contact_name=user.full_name,
            email=user.email,
            industry=org.industry,
            location=org.location,
            approval_status=org.approval_status,
            approval_note=org.approval_note,
            reviewed_at=org.reviewed_at,
            reviewed_by=org.reviewed_by,
        )
