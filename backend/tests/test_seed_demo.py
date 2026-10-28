"""Tests for demo seed idempotency and production guards."""

import os
import sys
from pathlib import Path

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from seed_demo import seed_demo
from seed_demo_reset import ALL_DEMO_EMAILS, reset_demo

from app.core.security import hash_password
from app.models.application import Application
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.course_resource import CourseResource
from app.models.internship import Internship
from app.models.notification import Notification
from app.models.submission import Submission
from app.models.user import User, UserRole


def test_seed_demo_refuses_in_production(real_db_session: Session) -> None:
    """Demo seed script refuses to run in production environment unless --force is set."""
    orig_env = os.environ.get("ENVIRONMENT")
    try:
        os.environ["ENVIRONMENT"] = "production"
        with pytest.raises(SystemExit) as exc:
            seed_demo(real_db_session, force=False)
        assert exc.value.code == 1

        seed_demo(real_db_session, force=True)
    finally:
        if orig_env is not None:
            os.environ["ENVIRONMENT"] = orig_env
        else:
            os.environ.pop("ENVIRONMENT", None)


def test_seed_demo_idempotency(real_db_session: Session) -> None:
    """Running seed_demo twice creates no duplicate users, courses, assignments, or apps."""
    seed_demo(real_db_session, force=True)

    def get_counts() -> dict[str, int]:
        c_titles = [
            "Introduction to Programming",
            "Database Systems",
            "Software Engineering",
        ]
        a_titles = [
            "Relational Schema Design & Normalization",
            "Advanced SQL Queries & Index Optimization",
            "ER Diagramming & Conceptual Modeling",
        ]
        return {
            "users": real_db_session.scalar(
                select(func.count(User.id)).where(User.email.in_(ALL_DEMO_EMAILS))
            )
            or 0,
            "courses": real_db_session.scalar(
                select(func.count(Course.id)).where(Course.title.in_(c_titles))
            )
            or 0,
            "assignments": real_db_session.scalar(
                select(func.count(Assignment.id)).where(Assignment.title.in_(a_titles))
            )
            or 0,
            "resources": real_db_session.scalar(
                select(func.count(CourseResource.id))
                .join(Course, CourseResource.course_id == Course.id)
                .where(Course.title.in_(c_titles))
            )
            or 0,
            "postings": real_db_session.scalar(
                select(func.count(Internship.id)).where(Internship.title.like("%Intern%"))
            )
            or 0,
            "submissions": real_db_session.scalar(
                select(func.count(Submission.id))
                .join(User, Submission.student_id == User.id)
                .where(User.email.in_(ALL_DEMO_EMAILS))
            )
            or 0,
            "apps": real_db_session.scalar(
                select(func.count(Application.id))
                .join(User, Application.student_id == User.id)
                .where(User.email.in_(ALL_DEMO_EMAILS))
            )
            or 0,
            "notifications": real_db_session.scalar(
                select(func.count(Notification.id))
                .join(User, Notification.user_id == User.id)
                .where(User.email.in_(ALL_DEMO_EMAILS))
            )
            or 0,
        }

    counts_first = get_counts()
    assert counts_first["users"] == 10
    assert counts_first["courses"] == 3
    assert counts_first["assignments"] == 3
    assert counts_first["resources"] == 6
    assert counts_first["postings"] == 8
    assert counts_first["submissions"] == 3
    assert counts_first["apps"] == 5
    assert counts_first["notifications"] == 12

    seed_demo(real_db_session, force=True)
    counts_second = get_counts()
    assert counts_first == counts_second


def test_reset_demo_preserves_non_demo_accounts(real_db_session: Session) -> None:
    """--reset-demo removes all demo accounts but preserves non-demo accounts."""
    seed_demo(real_db_session, force=True)

    non_demo = User(
        email="persistent.faculty@university.edu",
        full_name="Prof. Persistent",
        role=UserRole.INSTRUCTOR,
        password_hash=hash_password("NonDemoPass123!"),
        is_active=True,
    )
    real_db_session.add(non_demo)
    real_db_session.commit()

    deleted_count = reset_demo(real_db_session, skip_confirm=True)
    assert deleted_count > 0

    remaining_demo = real_db_session.scalars(
        select(User).where(User.email.in_(ALL_DEMO_EMAILS))
    ).all()
    assert len(list(remaining_demo)) == 0

    survivor = real_db_session.scalar(
        select(User).where(User.email == "persistent.faculty@university.edu")
    )
    assert survivor is not None
    assert survivor.full_name == "Prof. Persistent"
