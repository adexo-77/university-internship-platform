"""Tests for the demo seed script ensuring idempotency, production guards, and login."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

# Add scripts directory to path to import seed functions
SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from seed_demo import DEMO_PASSWORD, seed_demo
from seed_demo_reset import ALL_DEMO_EMAILS, reset_demo

from app.core.security import hash_password
from app.models.application import Application
from app.models.assignment import Assignment
from app.models.course import Course
from app.models.internship import Internship
from app.models.organization_profile import OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.submission import Submission
from app.models.user import User, UserRole

DEMO_ACCOUNTS = [
    ("demo.admin@example.com", "admin", "/api/dashboard/admin"),
    ("demo.instructor@example.com", "instructor", "/api/dashboard/instructor"),
    ("demo.student@example.com", "student", "/api/dashboard/student"),
    ("demo.student2@example.com", "student", "/api/dashboard/student"),
    ("demo.org@example.com", "organization", "/api/dashboard/organization"),
    ("demo.neworg@example.com", "organization", "/api/dashboard/organization"),
]


def test_seed_demo_refuses_in_production(real_db_session: Session) -> None:
    """Demo seed script refuses to run in production environment unless --force is set."""
    orig_env = os.environ.get("ENVIRONMENT")
    try:
        os.environ["ENVIRONMENT"] = "production"
        with pytest.raises(SystemExit) as exc:
            seed_demo(real_db_session, force=False)
        assert exc.value.code == 1

        # With force=True, it succeeds even in production
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
        return {
            "users": real_db_session.scalar(
                select(func.count(User.id)).where(User.email.like("demo.%"))
            )
            or 0,
            "courses": real_db_session.scalar(
                select(func.count(Course.id)).where(
                    Course.title.in_(["Web Architecture", "Cloud DevOps"])
                )
            )
            or 0,
            "assignments": real_db_session.scalar(
                select(func.count(Assignment.id)).where(
                    Assignment.title.in_(
                        ["Microservices Design", "Capstone Project", "Security & Auth"]
                    )
                )
            )
            or 0,
            "postings": real_db_session.scalar(
                select(func.count(Internship.id)).where(Internship.title.like("%Intern%"))
            )
            or 0,
            "submissions": real_db_session.scalar(
                select(func.count(Submission.id))
                .join(User, Submission.student_id == User.id)
                .where(User.email.like("demo.student%"))
            )
            or 0,
            "apps": real_db_session.scalar(
                select(func.count(Application.id))
                .join(User, Application.student_id == User.id)
                .where(User.email.like("demo.student%"))
            )
            or 0,
        }

    counts_first = get_counts()
    assert counts_first["users"] == 6
    assert counts_first["courses"] == 2
    assert counts_first["assignments"] == 3
    assert counts_first["postings"] == 6
    assert counts_first["submissions"] == 2
    assert counts_first["apps"] == 5

    # Run a second time
    seed_demo(real_db_session, force=True)
    counts_second = get_counts()
    assert counts_first == counts_second


def test_demo_accounts_login_and_dashboards(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Every seeded demo account can log in and access their role dashboard with 200 OK."""
    seed_demo(real_db_session, force=True)

    for email, _expected_role, dashboard_path in DEMO_ACCOUNTS:
        login_resp = real_db_client.post(
            "/api/auth/login",
            json={"email": email, "password": DEMO_PASSWORD},
        )
        assert login_resp.status_code == 200, f"Login failed for {email}: {login_resp.text}"

        dash_resp = real_db_client.get(dashboard_path)
        assert dash_resp.status_code == 200, f"Dashboard failed for {email}: {dash_resp.text}"
        data = dash_resp.json()
        assert isinstance(data, dict)

        # Logout before testing the next account
        real_db_client.post("/api/auth/logout")


def test_demo_profile_completeness_and_approval_states(
    real_db_session: Session,
) -> None:
    """Verify demo.student is complete, demo.student2 incomplete, and org approvals."""
    seed_demo(real_db_session, force=True)

    s1 = real_db_session.scalar(select(User).where(User.email == "demo.student@example.com"))
    assert s1 is not None
    sp1 = real_db_session.scalar(select(StudentProfile).where(StudentProfile.user_id == s1.id))
    assert sp1 is not None and sp1.university and sp1.department and len(sp1.skills) > 0

    s2 = real_db_session.scalar(select(User).where(User.email == "demo.student2@example.com"))
    assert s2 is not None
    sp2 = real_db_session.scalar(select(StudentProfile).where(StudentProfile.user_id == s2.id))
    assert sp2 is not None and not sp2.university and not sp2.department and len(sp2.skills) == 0

    org = real_db_session.scalar(select(User).where(User.email == "demo.org@example.com"))
    assert org is not None
    op = real_db_session.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == org.id)
    )
    assert op is not None and op.approval_status.value == "approved"

    neworg = real_db_session.scalar(select(User).where(User.email == "demo.neworg@example.com"))
    assert neworg is not None
    nop = real_db_session.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == neworg.id)
    )
    assert nop is not None and nop.approval_status.value == "pending"


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
