"""Application model representing a student application to an internship posting."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.internship import Internship
    from app.models.user import User


class ApplicationStatus(enum.StrEnum):
    """Allowed status states for an internship application."""

    SUBMITTED = "submitted"
    SHORTLISTED = "shortlisted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    """An application submitted by a student for an internship posting."""

    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("posting_id", "student_id", name="uq_applications_posting_student"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    posting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("internship_postings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cover_letter: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(
            ApplicationStatus,
            name="application_status",
            native_enum=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        server_default="submitted",
    )
    decision_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
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

    posting: Mapped["Internship"] = relationship("Internship", back_populates="applications")
    student: Mapped["User"] = relationship("User", back_populates="applications")
