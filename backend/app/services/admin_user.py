"""Domain service implementing administrator user management and account controls."""

from sqlalchemy import delete, func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictException,
    EmailAlreadyExistsException,
    NotFoundException,
)
from app.core.security import hash_password
from app.models.notification import NotificationKind
from app.models.session import Session as SessionModel
from app.models.user import User, UserRole
from app.schemas.admin_user import (
    AdminUserCreateRequest,
    AdminUserListResponse,
    AdminUserResponse,
)
from app.services.notification import create_notification


class AdminUserService:
    """Administrator user management business logic."""

    @staticmethod
    def list_users(
        db: Session,
        q: str | None = None,
        role: UserRole | None = None,
        is_active: bool | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> AdminUserListResponse:
        """List and search user accounts with role and active status filters."""
        clamped_limit = min(max(limit, 1), 100)
        clamped_offset = max(offset, 0)

        stmt = select(User)
        count_stmt = select(func.count(User.id))

        if role is not None:
            stmt = stmt.where(User.role == role)
            count_stmt = count_stmt.where(User.role == role)

        if is_active is not None:
            stmt = stmt.where(User.is_active == is_active)
            count_stmt = count_stmt.where(User.is_active == is_active)

        if q and q.strip():
            term = f"%{q.strip()}%"
            search_clause = or_(
                User.full_name.ilike(term),
                User.email.ilike(term),
            )
            stmt = stmt.where(search_clause)
            count_stmt = count_stmt.where(search_clause)

        total = db.scalar(count_stmt) or 0
        users = db.scalars(
            stmt.order_by(User.created_at.desc()).offset(clamped_offset).limit(clamped_limit)
        ).all()

        items = [AdminUserResponse.model_validate(u) for u in users]
        return AdminUserListResponse(
            items=items,
            total=total,
            limit=clamped_limit,
            offset=clamped_offset,
        )

    @staticmethod
    def create_user(db: Session, payload: AdminUserCreateRequest) -> User:
        """Create an instructor or admin account with normalized credentials."""
        existing_user = db.scalar(select(User).where(User.email == payload.email))
        if existing_user is not None:
            raise EmailAlreadyExistsException()

        target_role = UserRole(payload.role.value)

        user = User(
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            role=target_role,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user_status(
        db: Session,
        user_id: int,
        is_active: bool,
        current_admin: User,
    ) -> User:
        """Update user active state with self-deactivation and last-admin guards."""
        target_user = db.scalar(select(User).where(User.id == user_id))
        if target_user is None:
            raise NotFoundException(message="User not found", code="USER_NOT_FOUND")

        # Guard: An admin cannot deactivate themselves
        if not is_active and target_user.id == current_admin.id:
            raise ConflictException(
                message="You cannot deactivate your own administrative account",
                code="SELF_DEACTIVATION_FORBIDDEN",
            )

        # Guard: The last active admin can never be deactivated
        if not is_active and target_user.role == UserRole.ADMIN and target_user.is_active:
            active_admin_count = (
                db.scalar(
                    select(func.count(User.id)).where(
                        User.role == UserRole.ADMIN,
                        User.is_active.is_(True),
                    )
                )
                or 0
            )
            if active_admin_count <= 1:
                raise ConflictException(
                    message="The last active administrator cannot be deactivated",
                    code="LAST_ADMIN_PROTECTED",
                )

        target_user.is_active = is_active

        # Deactivating deletes all of that user's sessions
        if not is_active:
            db.execute(delete(SessionModel).where(SessionModel.user_id == target_user.id))

        db.commit()
        db.refresh(target_user)
        return target_user

    @staticmethod
    def reset_user_password(
        db: Session,
        user_id: int,
        new_password: str,
        admin_id: int | None = None,
    ) -> None:
        """Reset user password and invalidate all of the user's active sessions."""
        target_user = db.scalar(select(User).where(User.id == user_id))
        if target_user is None:
            raise NotFoundException(message="User not found", code="USER_NOT_FOUND")

        target_user.password_hash = hash_password(new_password)
        db.execute(delete(SessionModel).where(SessionModel.user_id == target_user.id))
        create_notification(
            db,
            user_id=target_user.id,
            actor_id=admin_id,
            kind=NotificationKind.PASSWORD_RESET,
            title="Password Reset",
            message="Your password was reset by an administrator.",
            link_path="/account",
        )
        db.commit()
