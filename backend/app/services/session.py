"""Domain service implementing session lifecycle, persistence, and resolution."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app.core.security import (
    SESSION_LIFETIME_SECONDS,
    generate_session_token,
    hash_session_token,
)
from app.models.session import Session as SessionModel
from app.models.user import User


class SessionService:
    """Session management and resolution logic."""

    @staticmethod
    def purge_expired_sessions(db: Session) -> int:
        """Purge expired sessions across all users."""
        now = datetime.now(UTC)
        result = db.execute(delete(SessionModel).where(SessionModel.expires_at <= now))
        db.commit()
        return int(result.rowcount)

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
        """Invalidate and delete the session matching the given raw token."""
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

        now = datetime.now(UTC)
        if session_record.expires_at <= now:
            db.delete(session_record)
            db.commit()
            return None

        if not session_record.user or not session_record.user.is_active:
            return None

        return session_record.user
