"""AI status and user consent service."""

from sqlalchemy.orm import Session

from app.core.clock import get_now
from app.core.config import Settings, settings
from app.models.user import User
from app.schemas.ai import AiStatusResponse
from app.services.ai_guard import get_remaining_quota


def get_ai_status(db: Session, user: User, cfg: Settings | None = None) -> AiStatusResponse:
    """Return AI availability, consent state, and remaining daily quota for the user."""
    active_cfg = cfg or settings
    remaining = get_remaining_quota(db, user.id, active_cfg)
    return AiStatusResponse(
        enabled=active_cfg.AI_ENABLED,
        consented=user.ai_consent_at is not None,
        consent_at=user.ai_consent_at,
        remaining_quota=remaining,
        daily_limit=active_cfg.AI_DAILY_LIMIT_PER_USER,
    )


def update_ai_consent(
    db: Session,
    user: User,
    consented: bool,
    cfg: Settings | None = None,
) -> AiStatusResponse:
    """Persist AI consent acceptance or withdrawal on the signed-in user."""
    user.ai_consent_at = get_now() if consented else None
    db.commit()
    db.refresh(user)
    return get_ai_status(db, user, cfg)
