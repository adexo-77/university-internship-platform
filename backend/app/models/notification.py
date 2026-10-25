"""Notification model representing in-app user notifications."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import urlsplit

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class NotificationKind(enum.StrEnum):
    """Constrained set of allowed notification event kinds."""

    SUBMISSION_GRADED = "submission_graded"
    APPLICATION_DECISION = "application_decision"
    ASSIGNMENT_CREATED = "assignment_created"
    FIRST_SUBMISSION = "first_submission"
    APPLICATION_RECEIVED = "application_received"
    INTERNSHIP_STATUS = "internship_status"
    ORGANIZATION_STATUS = "organization_status"
    ORGANIZATION_REGISTERED = "organization_registered"
    INTERNSHIP_SUBMITTED = "internship_submitted"
    PASSWORD_RESET = "password_reset"


class Notification(Base):
    """An in-app notification delivered to a user."""

    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_user_read_created", "user_id", "read_at", "created_at"),
        CheckConstraint(
            "link_path LIKE '/%' AND link_path NOT LIKE '//%' AND link_path NOT LIKE '%://%'",
            name="ck_notifications_link_path_internal",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    kind: Mapped[NotificationKind] = mapped_column(
        Enum(
            NotificationKind,
            name="notification_kind",
            native_enum=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    message: Mapped[str] = mapped_column(String(300), nullable=False)
    link_path: Mapped[str] = mapped_column(String(500), nullable=False)
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
    )

    @validates("link_path")
    def validate_link_path(self, _key: str, value: str) -> str:
        """Enforce internal link format starting with '/' and without scheme/host."""
        if not value or not value.startswith("/") or value.startswith("//"):
            raise ValueError("link_path must start with '/' and cannot be protocol-relative")
        parsed = urlsplit(value)
        if parsed.scheme or parsed.netloc:
            raise ValueError("link_path must be an internal path and cannot contain scheme or host")
        return value
