"""AI status and consent endpoints for authenticated users."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.ai import AiConsentRequest, AiStatusResponse
from app.services.ai import get_ai_status, update_ai_consent

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/status", response_model=AiStatusResponse, status_code=status.HTTP_200_OK)
def read_ai_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AiStatusResponse:
    """Return AI availability, user consent status, and remaining daily quota."""
    return get_ai_status(db, current_user)


@router.put("/consent", response_model=AiStatusResponse, status_code=status.HTTP_200_OK)
def set_ai_consent(
    payload: AiConsentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AiStatusResponse:
    """Accept or withdraw AI assistance consent for the signed-in user."""
    return update_ai_consent(db, current_user, payload.consented)
