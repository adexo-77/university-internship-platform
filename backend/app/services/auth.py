"""Domain service implementing authentication, session management, and credential verification."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import EmailAlreadyExistsException, InvalidCredentialsException
from app.core.security import (
    SESSION_LIFETIME_SECONDS,
    generate_session_token,
    hash_password,
    hash_session_token,
    verify_dummy_password,
    verify_password,
)
from app.models.session import Session as SessionModel
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    """Authentication and session management business logic."""

    @staticmethod
    def register(db: Session, request: RegisterRequest) -> tuple[User, str]:
        """Register a new user account with student or organization role.

        Raises:
            EmailAlreadyExistsException: If email is already registered.
        """
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
        db.add(user)
        db.commit()
        db.refresh(user)

        _, raw_token = AuthService.create_session(db=db, user_id=user.id)
        return user, raw_token

    @staticmethod
    def authenticate(db: Session, request: LoginRequest) -> tuple[User, str]:
        """Authenticate user credentials and create a session.

        Always performs constant-time hash verification even for non-existent users
        to prevent timing attacks from revealing existing emails.

        Raises:
            InvalidCredentialsException: On unknown email, wrong password, or inactive user.
        """
        user = db.scalar(select(User).where(User.email == request.email))

        if user is None:
            verify_dummy_password(request.password)
            raise InvalidCredentialsException()

        is_valid = verify_password(request.password, user.password_hash)
        if not is_valid or not user.is_active:
            raise InvalidCredentialsException()

        _, raw_token = AuthService.create_session(db=db, user_id=user.id)
        return user, raw_token

    @staticmethod
    def create_session(db: Session, user_id: int) -> tuple[SessionModel, str]:
        """Create a new session record storing only the SHA-256 hash of the token."""
        raw_token = generate_session_token()
        token_hash = hash_session_token(raw_token)
        expires_at = datetime.now(UTC) + timedelta(seconds=SESSION_LIFETIME_SECONDS)

        session_record = SessionModel(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        db.add(session_record)
        db.commit()
        db.refresh(session_record)

        return session_record, raw_token

    @staticmethod
    def delete_session(db: Session, raw_token: str | None) -> None:
        """Invalidate and delete the session matching the given raw token.

        Safe to call when signed out or when raw_token is missing or empty.
        """
        if not raw_token:
            return

        token_hash = hash_session_token(raw_token)
        db.execute(delete(SessionModel).where(SessionModel.token_hash == token_hash))
        db.commit()

    @staticmethod
    def resolve_current_user(db: Session, raw_token: str | None) -> User | None:
        """Resolve current active user from session token cookie, expiring stale sessions."""
        if not raw_token:
            return None

        token_hash = hash_session_token(raw_token)
        stmt = (
            select(SessionModel)
            .options(joinedload(SessionModel.user))
            .where(SessionModel.token_hash == token_hash)
        )
        session_record = db.scalar(stmt)
        if session_record is None:
            return None

        # Check session expiry
        now = datetime.now(UTC)
        if session_record.expires_at <= now:
            db.delete(session_record)
            db.commit()
            return None

        # Verify associated user is active
        if not session_record.user or not session_record.user.is_active:
            return None

        return session_record.user
