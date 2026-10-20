"""Internship model representing organization-created internship postings."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.user import User


class InternshipWorkMode(enum.StrEnum):
    """Allowed work modes for an internship posting."""

    ONSITE = "onsite"
    REMOTE = "remote"
    HYBRID = "hybrid"


class InternshipStatus(enum.StrEnum):
    """Lifecycle status for an internship posting."""

    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    OPEN = "open"
    REJECTED = "rejected"
    CLOSED = "closed"


class Internship(Base):
    """An internship posting created by an organization."""

    __tablename__ = "internship_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    work_mode: Mapped[InternshipWorkMode] = mapped_column(
        Enum(
            InternshipWorkMode,
            name="internship_work_mode",
            native_enum=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    duration_weeks: Mapped[int | None] = mapped_column(Integer, nullable=True)
    application_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    status: Mapped[InternshipStatus] = mapped_column(
        Enum(
            InternshipStatus,
            name="internship_status",
            native_enum=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        server_default="draft",
    )
    review_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    reviewed_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    organization: Mapped["User"] = relationship(
        "User",
        foreign_keys=[organization_id],
        back_populates="internships",
    )
    reviewer: Mapped["User | None"] = relationship(
        "User",
        foreign_keys=[reviewed_by],
    )
    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="posting",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
