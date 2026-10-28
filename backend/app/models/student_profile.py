"""Student profile model representing academic details, skills, and bio."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class StudentProfile(Base):
    """Student profile information."""

    __tablename__ = "student_profiles"
    __table_args__ = (
        CheckConstraint(
            "year_of_study IS NULL OR (year_of_study >= 1 AND year_of_study <= 6)",
            name="check_student_year_of_study",
        ),
        UniqueConstraint("user_id", name="uq_student_profiles_user_id"),
        Index("ix_student_profiles_user_id", "user_id", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    university: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    year_of_study: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bio: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    skills: Mapped[list[str]] = mapped_column(
        ARRAY(String(40)),
        nullable=False,
        default=list,
        server_default="{}",
    )
    preferred_work_modes: Mapped[list[str]] = mapped_column(
        ARRAY(String(20)),
        nullable=False,
        default=list,
        server_default="{}",
    )
    preferred_location: Mapped[str | None] = mapped_column(String(80), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="student_profile")
