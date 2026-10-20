"""Admin user management API router."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_roles
from app.models.user import User, UserRole
from app.schemas.admin_user import (
    AdminUserCreateRequest,
    AdminUserListResponse,
    AdminUserPasswordResetRequest,
    AdminUserResponse,
    AdminUserUpdateRequest,
)
from app.services.admin_user import AdminUserService

router = APIRouter(prefix="/admin/users", tags=["admin-users"])
require_admin = require_roles(UserRole.ADMIN)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=AdminUserListResponse,
    summary="List and search users",
)
def list_users(
    q: str | None = Query(default=None, description="Search by name or email"),
    role: UserRole | None = Query(default=None, description="Filter by account role"),
    is_active: bool | None = Query(default=None, description="Filter by active status"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    offset: int = Query(default=0, ge=0, description="Pagination offset"),
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminUserListResponse:
    """Retrieve paginated user directory with search and filtering."""
    return AdminUserService.list_users(
        db=db,
        q=q,
        role=role,
        is_active=is_active,
        limit=limit,
        offset=offset,
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=AdminUserResponse,
    summary="Provision instructor or admin user",
)
def create_user(
    payload: AdminUserCreateRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    """Create a new instructor or administrative user account."""
    return AdminUserService.create_user(db=db, payload=payload)


@router.patch(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=AdminUserResponse,
    summary="Update user active status",
)
def update_user_status(
    user_id: int,
    payload: AdminUserUpdateRequest,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> User:
    """Activate or deactivate a user account with administrative protections."""
    return AdminUserService.update_user_status(
        db=db,
        user_id=user_id,
        is_active=payload.is_active,
        current_admin=current_admin,
    )


@router.put(
    "/{user_id}/password",
    status_code=status.HTTP_200_OK,
    summary="Reset user password",
)
def reset_user_password(
    user_id: int,
    payload: AdminUserPasswordResetRequest,
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """Reset user password and invalidate all of the user's active sessions."""
    AdminUserService.reset_user_password(
        db=db,
        user_id=user_id,
        new_password=payload.password,
    )
    return {"message": "Password reset successfully"}
