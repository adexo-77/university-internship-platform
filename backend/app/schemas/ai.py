"""Pydantic schemas for AI status and user consent."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AiStatusResponse(BaseModel):
    """Publicly safe AI status and daily quota summary for the signed-in user."""

    enabled: bool
    consented: bool
    consent_at: datetime | None = None
    remaining_quota: int
    daily_limit: int


class AiConsentRequest(BaseModel):
    """Request payload to accept or withdraw AI assistance consent."""

    model_config = ConfigDict(extra="forbid")

    consented: bool
