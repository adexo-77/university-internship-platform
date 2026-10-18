"""Enrollment model representing student enrollment in a course."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User


class Enrollment(Base):
    """Enrollment record linking a student to an enrolled course."""

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("course_id", "student_id", name="uq_enrollments_course_student"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    student_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    enrolled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    course: Mapped["Course"] = relationship("Course", back_populates="enrollments")
    student: Mapped["User"] = relationship("User", back_populates="enrollments")
