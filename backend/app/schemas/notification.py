"""Pydantic schemas for notifications."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.notification import NotificationKind


class NotificationResponse(BaseModel):
    """Notification item returned by endpoints."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: int
    user_id: int
    kind: NotificationKind
    title: str
    message: str
    link_path: str
    read_at: datetime | None = None
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Paginated list of notifications with unread count."""

    model_config = ConfigDict(extra="forbid")

    items: list[NotificationResponse]
    total: int
    unread_count: int
    limit: int
    offset: int


class UnreadCountResponse(BaseModel):
    """Response containing unread notification count."""

    model_config = ConfigDict(extra="forbid")

    unread_count: int


class MarkAllReadResponse(BaseModel):
    """Response acknowledging bulk read operation."""

    model_config = ConfigDict(extra="forbid")

    updated_count: int
