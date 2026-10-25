"""Tests for administrative and organization lifecycle notification events."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.internship import InternshipStatus
from app.models.notification import Notification, NotificationKind
from app.models.organization_profile import ApprovalStatus, OrganizationProfile
from app.models.user import UserRole
from app.schemas.admin_internship import InternshipReviewRequest
from app.schemas.admin_organization import AdminOrganizationApprovalRequest
from app.schemas.auth import RegisterRequest
from app.services.admin_internship import review_internship
from app.services.admin_organization import AdminOrganizationService
from app.services.admin_user import AdminUserService
from app.services.auth import AuthService
from app.services.internship import submit_internship
from tests.factories import create_test_internship, create_test_user


def test_organization_status_change_notifies_organization(real_db_session: Session) -> None:
    """Admin updating organization approval status notifies the organization with review note."""
    db = real_db_session
    admin = create_test_user(db, "admin_org_notif@example.com", UserRole.ADMIN)
    org_user = create_test_user(db, "org_status_notif@example.com", UserRole.ORGANIZATION)
    db.add(
        OrganizationProfile(
            user_id=org_user.id,
            organization_name="Fintech Inc",
            approval_status=ApprovalStatus.PENDING,
        )
    )
    db.commit()

    payload = AdminOrganizationApprovalRequest(
        approval_status=ApprovalStatus.APPROVED,
        approval_note="Verified corporate registration document.",
    )
    AdminOrganizationService.update_approval(db, org_user.id, payload, admin)

    notif = db.scalar(
        select(Notification).where(
            Notification.user_id == org_user.id,
            Notification.kind == NotificationKind.ORGANIZATION_STATUS,
        )
    )
    assert notif is not None
    assert "Organization Status: Approved" in notif.title
    assert "Verified corporate registration document." in notif.message
    assert notif.link_path == "/profile"

    # Admin was not notified
    assert (
        db.scalar(
            select(Notification).where(
                Notification.user_id == admin.id,
                Notification.kind == NotificationKind.ORGANIZATION_STATUS,
            )
        )
        is None
    )


def test_organization_registered_notifies_admins(real_db_session: Session) -> None:
    """A newly registered organization triggers notification to all active admins."""
    db = real_db_session
    admin1 = create_test_user(db, "adm1_reg_notif@example.com", UserRole.ADMIN)
    admin2 = create_test_user(db, "adm2_reg_notif@example.com", UserRole.ADMIN)

    reg_payload = RegisterRequest(
        email="new_org_reg@example.com",
        password="Password123!",
        full_name="Alice Recruiter",
        role=UserRole.ORGANIZATION,
        organization_name="Quantum Innovations",
    )
    user, _ = AuthService.register(db, reg_payload)

    for admin in (admin1, admin2):
        n = db.scalar(
            select(Notification).where(
                Notification.user_id == admin.id,
                Notification.kind == NotificationKind.ORGANIZATION_REGISTERED,
            )
        )
        assert n is not None
        assert "Quantum Innovations" in n.title
        assert n.link_path == "/admin/organizations"

    # Registered user was not notified
    assert db.scalar(select(Notification).where(Notification.user_id == user.id)) is None


def test_internship_submitted_notifies_admins(real_db_session: Session) -> None:
    """Submitting an internship for review notifies all active platform admins."""
    db = real_db_session
    admin = create_test_user(db, "adm_post_notif@example.com", UserRole.ADMIN)
    org = create_test_user(db, "org_post_notif@example.com", UserRole.ORGANIZATION)
    posting = create_test_internship(
        db,
        org,
        title="Cloud Architect Intern",
        status=InternshipStatus.DRAFT,
        application_deadline=datetime.now(UTC) + timedelta(days=30),
    )

    submit_internship(db, posting.id, org)

    admin_notif = db.scalar(
        select(Notification).where(
            Notification.user_id == admin.id,
            Notification.kind == NotificationKind.INTERNSHIP_SUBMITTED,
        )
    )
    assert admin_notif is not None
    assert "Internship Review: Cloud Architect Intern" in admin_notif.title
    assert admin_notif.link_path == "/admin/internship-reviews"

    # Submitting org was not notified
    assert (
        db.scalar(
            select(Notification).where(
                Notification.user_id == org.id,
                Notification.kind == NotificationKind.INTERNSHIP_SUBMITTED,
            )
        )
        is None
    )


def test_internship_review_decisions_notify_organization(real_db_session: Session) -> None:
    """Approving, rejecting, and taking down postings notifies the organization with notes."""
    db = real_db_session
    admin = create_test_user(db, "adm_rev_dec@example.com", UserRole.ADMIN)
    org = create_test_user(db, "org_rev_dec@example.com", UserRole.ORGANIZATION)

    p1 = create_test_internship(
        db, org, title="Data Science Intern", status=InternshipStatus.PENDING_REVIEW
    )
    review_internship(
        db, p1.id, admin.id, InternshipReviewRequest(decision="approved", review_note="Looks solid")
    )
    n1 = db.scalar(
        select(Notification).where(
            Notification.user_id == org.id,
            Notification.title == "Posting Approved: Data Science Intern",
        )
    )
    assert (
        n1 is not None and "Looks solid" in n1.message and n1.link_path == f"/internships/{p1.id}"
    )

    p2 = create_test_internship(
        db, org, title="Marketing Intern", status=InternshipStatus.PENDING_REVIEW
    )
    review_internship(
        db, p2.id, admin.id, InternshipReviewRequest(decision="rejected", review_note="Vague")
    )
    n2 = db.scalar(
        select(Notification).where(
            Notification.user_id == org.id,
            Notification.title == "Posting Rejected: Marketing Intern",
        )
    )
    assert n2 is not None and "Vague" in n2.message

    p3 = create_test_internship(db, org, title="DevOps Intern", status=InternshipStatus.OPEN)
    review_internship(
        db, p3.id, admin.id, InternshipReviewRequest(decision="rejected", review_note="Policy")
    )
    n3 = db.scalar(
        select(Notification).where(
            Notification.user_id == org.id,
            Notification.title == "Posting Taken down: DevOps Intern",
        )
    )
    assert n3 is not None and "Policy" in n3.message


def test_admin_reset_password_notifies_user_unless_self(real_db_session: Session) -> None:
    """Admin password reset notifies the affected user; admin self-reset does not notify self."""
    db = real_db_session
    admin = create_test_user(db, "adm_pw_reset@example.com", UserRole.ADMIN)
    target = create_test_user(db, "target_pw_reset@example.com", UserRole.STUDENT)

    AdminUserService.reset_user_password(
        db=db, user_id=target.id, new_password="NewSecretPassword123!", admin_id=admin.id
    )
    target_notif = db.scalar(
        select(Notification).where(
            Notification.user_id == target.id, Notification.kind == NotificationKind.PASSWORD_RESET
        )
    )
    assert target_notif is not None
    assert target_notif.title == "Password Reset" and target_notif.link_path == "/account"

    admin_notifs = list(
        db.scalars(
            select(Notification).where(
                Notification.user_id == admin.id,
                Notification.kind == NotificationKind.PASSWORD_RESET,
            )
        )
    )
    assert len(admin_notifs) == 0

    AdminUserService.reset_user_password(
        db=db, user_id=admin.id, new_password="AdminNewPassword123!", admin_id=admin.id
    )
    assert (
        db.scalar(
            select(Notification).where(
                Notification.user_id == admin.id,
                Notification.kind == NotificationKind.PASSWORD_RESET,
            )
        )
        is None
    )
