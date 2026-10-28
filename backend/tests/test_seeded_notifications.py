"""Integration tests verifying seeded demo notifications validity and link accessibility."""

import sys
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from seed_demo import DEMO_PASSWORD, seed_demo

from app.models.application import Application
from app.models.assignment import Assignment
from app.models.internship import Internship, InternshipStatus
from app.models.notification import Notification, NotificationKind
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.submission import Submission
from app.models.user import User, UserRole
from tests.factories import login_test_user


def _resolve_api_url(link_path: str, recipient: User) -> str:
    if link_path.startswith("/assignments/"):
        return f"/api{link_path}"
    if link_path.startswith("/applications/"):
        return f"/api{link_path}"
    if link_path.startswith("/internships/"):
        return f"/api{link_path}"
    if link_path == "/admin/organizations":
        return "/api/admin/organizations"
    if link_path == "/admin/internship-reviews":
        return "/api/admin/internships"
    if link_path == "/profile":
        if recipient.role == UserRole.ORGANIZATION:
            return "/api/organizations/me"
        return "/api/students/me"
    return f"/api{link_path}"


def _verify_referenced_entity_and_values(
    db: Session,
    notif: Notification,
    recipient: User,
) -> None:
    text = f"{notif.title} {notif.message}".lower()

    if notif.link_path.startswith("/assignments/"):
        aid = int(notif.link_path.split("/")[-1])
        assignment = db.get(Assignment, aid)
        assert assignment is not None, f"Referenced assignment {aid} not found"
        assert assignment.title.lower() in text

        if notif.kind == NotificationKind.SUBMISSION_GRADED:
            sub = db.scalar(
                select(Submission).where(
                    Submission.assignment_id == aid,
                    Submission.student_id == recipient.id,
                )
            )
            assert sub is not None, f"Submission for assignment {aid} not found"
            assert sub.grade is not None
            expected_fraction = f"{sub.grade}/{assignment.max_points}"
            assert expected_fraction in f"{notif.title} {notif.message}"

    elif notif.link_path.startswith("/applications/"):
        appid = int(notif.link_path.split("/")[-1])
        app = db.get(Application, appid)
        assert app is not None, f"Referenced application {appid} not found"
        posting = db.get(Internship, app.posting_id)
        assert posting is not None
        assert posting.title.lower() in text
        assert app.status.value.lower() in text
        if app.decision_message:
            assert app.decision_message in notif.message

    elif notif.link_path.startswith("/internships/"):
        pid = int(notif.link_path.split("/")[-1])
        posting = db.get(Internship, pid)
        assert posting is not None, f"Referenced posting {pid} not found"
        assert posting.title.lower() in text
        if notif.kind == NotificationKind.INTERNSHIP_STATUS:
            assert posting.status.value in ["open", "approved"]

    elif notif.link_path == "/admin/organizations":
        pending_org = db.scalar(
            select(OrganizationProfile).where(
                OrganizationProfile.approval_status == ApprovalStatus.PENDING
            )
        )
        assert pending_org is not None, "Pending organization not found"
        assert pending_org.organization_name.lower() in text

    elif notif.link_path == "/admin/internship-reviews":
        pending_posting = db.scalar(
            select(Internship).where(Internship.status == InternshipStatus.PENDING_REVIEW)
        )
        assert pending_posting is not None, "Pending internship review not found"
        assert pending_posting.title.lower() in text

    elif notif.link_path == "/profile":
        if recipient.role == UserRole.ORGANIZATION:
            org_prof = db.scalar(
                select(OrganizationProfile).where(OrganizationProfile.user_id == recipient.id)
            )
            assert org_prof is not None, "Organization profile not found"
            if notif.kind == NotificationKind.ORGANIZATION_STATUS:
                assert org_prof.approval_status == ApprovalStatus.APPROVED
                assert org_prof.approval_status.value in text


def test_seeded_notifications_entities_links_and_values(
    real_db_client: TestClient,
    real_db_session: Session,
) -> None:
    """Verify seeded notifications refer to real entities, open with 200, and match values."""
    seed_demo(real_db_session, force=True)

    notifications = list(real_db_session.scalars(select(Notification)).all())
    assert len(notifications) == 12, f"Expected 12 seeded notifications, got {len(notifications)}"

    for notif in notifications:
        recipient = real_db_session.get(User, notif.user_id)
        assert recipient is not None, f"Recipient user {notif.user_id} not found"

        # 1. Referenced entity exists and grade/status equals stored value
        _verify_referenced_entity_and_values(real_db_session, notif, recipient)

        # 2. Recipient may open the link via API and receives 200 OK
        real_db_client.cookies.clear()
        login_test_user(real_db_client, recipient.email, DEMO_PASSWORD)

        api_url = _resolve_api_url(notif.link_path, recipient)
        resp = real_db_client.get(api_url)
        assert resp.status_code == 200, (
            f"Recipient {recipient.email} ({recipient.role.value}) failed to open {api_url} "
            f"for notification '{notif.title}': status={resp.status_code}"
        )
        real_db_client.post("/api/auth/logout")
