"""Pydantic schemas for student achievement badges."""

from pydantic import BaseModel, ConfigDict


class BadgeProgress(BaseModel):
    """Current progress and target count for countable achievement badges."""

    model_config = ConfigDict(extra="forbid")

    current: int
    target: int


class BadgeResponse(BaseModel):
    """Achievement badge item representing student milestone accomplishment."""

    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    earned: bool
    progress: BadgeProgress | None = None
