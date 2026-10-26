"""Tests for demo accounts login, profile completeness, and notifications."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from seed_demo import DEMO_PASSWORD, seed_demo

from app.models.organization_profile import OrganizationProfile
from app.models.student_profile import StudentProfile
from app.models.user import User

DEMO_ACCOUNTS = [
    ("mulugeta.assefa@example.com", "admin", "/api/dashboard/admin"),
    ("selamawit.tadesse@example.com", "coordinator", "/api/dashboard/coordinator"),
    ("tadesse.bekele@example.com", "instructor", "/api/dashboard/instructor"),
    ("hana.worku@example.com", "instructor", "/api/dashboard/instructor"),
    ("abel.tesfaye@example.com", "student", "/api/dashboard/student"),
    ("meron.girma@example.com", "student", "/api/dashboard/student"),
    ("dawit.lemma@example.com", "student", "/api/dashboard/student"),
    ("yohannes.haile@example.com", "organization", "/api/dashboard/organization"),
    ("rahel.desta@example.com", "organization", "/api/dashboard/organization"),
    ("eyob.kassa@example.com", "organization", "/api/dashboard/organization"),
]


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

        real_db_client.post("/api/auth/logout")


def test_demo_profile_completeness_and_approval_states(
    real_db_session: Session,
) -> None:
    """Verify Abel/Meron complete, Dawit incomplete, and organization approval states."""
    seed_demo(real_db_session, force=True)

    s1 = real_db_session.scalar(select(User).where(User.email == "abel.tesfaye@example.com"))
    assert s1 is not None
    sp1 = real_db_session.scalar(select(StudentProfile).where(StudentProfile.user_id == s1.id))
    assert sp1 is not None and sp1.university == "Jimma University" and len(sp1.skills) > 0

    s2 = real_db_session.scalar(select(User).where(User.email == "meron.girma@example.com"))
    assert s2 is not None
    sp2 = real_db_session.scalar(select(StudentProfile).where(StudentProfile.user_id == s2.id))
    assert sp2 is not None and sp2.university == "Jimma University" and len(sp2.skills) > 0

    s3 = real_db_session.scalar(select(User).where(User.email == "dawit.lemma@example.com"))
    assert s3 is not None
    sp3 = real_db_session.scalar(select(StudentProfile).where(StudentProfile.user_id == s3.id))
    assert sp3 is not None and len(sp3.skills) == 0

    coord = real_db_session.scalar(
        select(User).where(User.email == "selamawit.tadesse@example.com")
    )
    assert coord is not None and coord.role.value == "coordinator"

    org1 = real_db_session.scalar(select(User).where(User.email == "yohannes.haile@example.com"))
    assert org1 is not None
    op1 = real_db_session.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == org1.id)
    )
    assert op1 is not None and op1.approval_status.value == "approved"

    org2 = real_db_session.scalar(select(User).where(User.email == "rahel.desta@example.com"))
    assert org2 is not None
    op2 = real_db_session.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == org2.id)
    )
    assert op2 is not None and op2.approval_status.value == "approved"

    org3 = real_db_session.scalar(select(User).where(User.email == "eyob.kassa@example.com"))
    assert org3 is not None
    op3 = real_db_session.scalar(
        select(OrganizationProfile).where(OrganizationProfile.user_id == org3.id)
    )
    assert op3 is not None and op3.approval_status.value == "pending"


def test_seeded_demo_notifications(real_db_client: TestClient, real_db_session: Session) -> None:
    """Demo accounts receive realistic notifications accessible via API."""
    seed_demo(real_db_session, force=True)
    resp = real_db_client.post(
        "/api/auth/login",
        json={"email": "abel.tesfaye@example.com", "password": DEMO_PASSWORD},
    )
    assert resp.status_code == 200
    res = real_db_client.get("/api/notifications")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3
    assert data["unread_count"] == 2
    real_db_client.post("/api/auth/logout")


def test_seeded_student_achievement_badges(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Verify Abel earns several achievement badges and Meron earns fewer."""
    seed_demo(real_db_session, force=True)

    # Abel's badges
    login_abel = real_db_client.post(
        "/api/auth/login",
        json={"email": "abel.tesfaye@example.com", "password": DEMO_PASSWORD},
    )
    assert login_abel.status_code == 200
    abel_badges_resp = real_db_client.get("/api/students/me/badges")
    assert abel_badges_resp.status_code == 200
    abel_badges = abel_badges_resp.json()

    abel_earned_ids = {b["id"] for b in abel_badges if b["earned"]}
    assert "first_submission" in abel_earned_ids
    assert "high_achiever" in abel_earned_ids
    assert "perfect_score" in abel_earned_ids
    assert "profile_complete" in abel_earned_ids
    assert "first_application" in abel_earned_ids
    assert "offer_accepted" in abel_earned_ids
    assert len(abel_earned_ids) == 6

    # Meron's badges
    real_db_client.post("/api/auth/logout")
    login_meron = real_db_client.post(
        "/api/auth/login",
        json={"email": "meron.girma@example.com", "password": DEMO_PASSWORD},
    )
    assert login_meron.status_code == 200
    meron_badges_resp = real_db_client.get("/api/students/me/badges")
    assert meron_badges_resp.status_code == 200
    meron_badges = meron_badges_resp.json()

    meron_earned_ids = {b["id"] for b in meron_badges if b["earned"]}
    assert "first_submission" in meron_earned_ids
    assert "profile_complete" in meron_earned_ids
    assert "first_application" in meron_earned_ids
    assert "offer_accepted" not in meron_earned_ids
    assert "perfect_score" not in meron_earned_ids
    assert len(meron_earned_ids) == 3

    assert len(abel_earned_ids) > len(meron_earned_ids)
    real_db_client.post("/api/auth/logout")
