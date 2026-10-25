"""Domain service implementing authentication, session management, and credential verification."""

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AppException,
    EmailAlreadyExistsException,
    InvalidCredentialsException,
)
from app.core.rate_limit import rate_limiter
from app.core.security import (
    hash_password,
    hash_session_token,
    verify_dummy_password,
    verify_password,
)
from app.models.notification import NotificationKind
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.session import Session as SessionModel
from app.models.student_profile import StudentProfile
from app.models.user import User, UserRole
from app.schemas.auth import ChangePasswordRequest, LoginRequest, RegisterRequest
from app.services.notification import create_notification
from app.services.session import SessionService


class AuthService:
    """Authentication and session management business logic."""

    purge_expired_sessions = staticmethod(SessionService.purge_expired_sessions)
    create_session = staticmethod(SessionService.create_session)
    delete_session = staticmethod(SessionService.delete_session)
    resolve_current_user = staticmethod(SessionService.resolve_current_user)

    @staticmethod
    def register(
        db: Session, request: RegisterRequest, client_ip: str = "127.0.0.1"
    ) -> tuple[User, str]:
        """Register a new user account with student or organization role.

        Creates an empty profile row for a student or an organization profile with
        organization_name in the same transaction. If either insert fails, nothing is saved.

        Raises:
            EmailAlreadyExistsException: If email is already registered.
            AppException (422): If organization registration lacks organization_name.
        """
        rate_limiter.check_and_record_register(client_ip=client_ip)
        existing_user = db.scalar(select(User).where(User.email == request.email))
        if existing_user is not None:
            raise EmailAlreadyExistsException()

        password_hash = hash_password(request.password)
        user = User(
            email=request.email,
            password_hash=password_hash,
            full_name=request.full_name,
            role=UserRole(request.role.value),
            is_active=True,
        )

        try:
            db.add(user)
            db.flush()

            if user.role == UserRole.STUDENT:
                student_profile = StudentProfile(user_id=user.id, skills=[])
                db.add(student_profile)
            elif user.role == UserRole.ORGANIZATION:
                org_name = request.organization_name.strip() if request.organization_name else ""
                if not org_name:
                    raise AppException(
                        message="Organization name is required.",
                        code="VALIDATION_ERROR",
                        status_code=422,
                    )
                org_profile = OrganizationProfile(
                    user_id=user.id,
                    organization_name=org_name,
                    approval_status=ApprovalStatus.PENDING,
                )
                db.add(org_profile)
                recipient_ids = list(
                    db.scalars(
                        select(User.id).where(
                            User.role.in_([UserRole.ADMIN, UserRole.COORDINATOR]),
                            User.is_active.is_(True),
                        )
                    )
                )
                for recipient_id in recipient_ids:
                    create_notification(
                        db,
                        user_id=recipient_id,
                        actor_id=user.id,
                        kind=NotificationKind.ORGANIZATION_REGISTERED,
                        title=f"New Organization: {org_name}",
                        message=f"Organization '{org_name}' registered and is pending approval.",
                        link_path="/admin/organizations",
                    )

            db.commit()
            db.refresh(user)
        except Exception:
            db.rollback()
            raise

        _, raw_token = AuthService.create_session(db=db, user_id=user.id)
        return user, raw_token

    @staticmethod
    def authenticate(
        db: Session, request: LoginRequest, client_ip: str = "127.0.0.1"
    ) -> tuple[User, str]:
        """Authenticate user credentials and create a session.

        Always performs constant-time hash verification even for non-existent users
        to prevent timing attacks from revealing existing emails.

        Raises:
            InvalidCredentialsException: On unknown email, wrong password, or inactive user.
        """
        rate_limiter.check_login_attempt(client_ip=client_ip, email=request.email)
        user = db.scalar(select(User).where(User.email == request.email))

        if user is None:
            rate_limiter.record_login_failure(client_ip=client_ip, email=request.email)
            verify_dummy_password(request.password)
            raise InvalidCredentialsException()

        is_valid = verify_password(request.password, user.password_hash)
        if not is_valid or not user.is_active:
            rate_limiter.record_login_failure(client_ip=client_ip, email=request.email)
            raise InvalidCredentialsException()

        rate_limiter.reset_login_failures(client_ip=client_ip, email=request.email)
        AuthService.purge_expired_sessions(db)
        _, raw_token = AuthService.create_session(db=db, user_id=user.id)
        return user, raw_token

    @staticmethod
    def change_password(
        db: Session,
        user: User,
        current_token: str | None,
        request: ChangePasswordRequest,
    ) -> None:
        """Change authenticated user password, invalidate all other sessions, and keep current."""
        rate_limiter.check_and_record_change_password(user_id=user.id)
        if not verify_password(request.current_password, user.password_hash):
            verify_dummy_password(request.current_password)
            raise InvalidCredentialsException()

        if verify_password(request.new_password, user.password_hash):
            raise AppException(
                message="New password must be different from current password.",
                code="SAME_PASSWORD",
                status_code=422,
            )

        user.password_hash = hash_password(request.new_password)

        if current_token:
            current_token_hash = hash_session_token(current_token)
            db.execute(
                delete(SessionModel).where(
                    SessionModel.user_id == user.id,
                    SessionModel.token_hash != current_token_hash,
                )
            )
        else:
            db.execute(delete(SessionModel).where(SessionModel.user_id == user.id))

        db.commit()
