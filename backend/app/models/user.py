"""User model representing platform accounts and roles."""

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.application import Application
    from app.models.course import Course
    from app.models.enrollment import Enrollment
    from app.models.internship import Internship
    from app.models.notification import Notification
    from app.models.organization_profile import OrganizationProfile
    from app.models.session import Session
    from app.models.student_profile import StudentProfile
    from app.models.submission import Submission


class UserRole(enum.StrEnum):
    """User account roles."""

    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ORGANIZATION = "organization"
    ADMIN = "admin"


class User(Base):
    """User account in the platform."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=True,
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    sessions: Mapped[list["Session"]] = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    student_profile: Mapped["StudentProfile | None"] = relationship(
        "StudentProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    organization_profile: Mapped["OrganizationProfile | None"] = relationship(
        "OrganizationProfile",
        foreign_keys="OrganizationProfile.user_id",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    courses: Mapped[list["Course"]] = relationship(
        "Course",
        back_populates="instructor",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        foreign_keys="Submission.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    graded_submissions: Mapped[list["Submission"]] = relationship(
        "Submission",
        foreign_keys="Submission.graded_by",
        back_populates="grader",
    )
    internships: Mapped[list["Internship"]] = relationship(
        "Internship",
        foreign_keys="Internship.organization_id",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    applications: Mapped[list["Application"]] = relationship(
        "Application",
        back_populates="student",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
