"""Tests for coordinator provisioning lifecycle, notifications, and dashboard metrics."""

from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.internship import InternshipStatus
from app.models.notification import Notification, NotificationKind
from app.models.user import UserRole
from app.schemas.auth import RegisterRequest
from app.services.auth import AuthService
from app.services.internship import submit_internship
from tests.factories import create_test_internship, create_test_user, login_test_user


def test_self_registration_cannot_create_coordinator(real_db_client: TestClient) -> None:
    """Public registration rejects role=coordinator with 422 Unprocessable Entity."""
    res = real_db_client.post(
        "/api/auth/register",
        json={
            "email": "hack_coord@example.com",
            "password": "Password123!",
            "full_name": "Wannabe Coordinator",
            "role": "coordinator",
        },
    )
    assert res.status_code == 422


def test_admin_can_create_coordinator_user(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Admin user endpoint successfully creates active user with coordinator role."""
    admin = create_test_user(real_db_session, "admin_coord_creator@example.com", UserRole.ADMIN)
    login_test_user(real_db_client, admin.email)

    create_res = real_db_client.post(
        "/api/admin/users",
        json={
            "email": "new_coord@example.com",
            "password": "Password123!",
            "full_name": "Selamawit Coordinator",
            "role": "coordinator",
        },
    )
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["role"] == "coordinator"
    assert data["email"] == "new_coord@example.com"

    # New coordinator can log in and view dashboard
    login_test_user(real_db_client, "new_coord@example.com")
    dash_res = real_db_client.get("/api/dashboard/coordinator")
    assert dash_res.status_code == 200


def test_notifications_reach_coordinators_and_admins(
    real_db_session: Session,
) -> None:
    """Platform events notify both admins and coordinators."""
    db = real_db_session
    admin = create_test_user(db, "notif_admin_dest@example.com", UserRole.ADMIN)
    coord = create_test_user(db, "notif_coord_dest@example.com", UserRole.COORDINATOR)
    org_user = create_test_user(db, "notif_org_owner@example.com", UserRole.ORGANIZATION)

    # 1. New organization registers
    AuthService.register(
        db,
        RegisterRequest(
            email="notif_brand_new_org@example.com",
            password="Password123!",
            full_name="New Recruiter",
            role=UserRole.ORGANIZATION,
            organization_name="Addis Tech Lab",
        ),
    )

    for recipient in (admin, coord):
        n = db.scalar(
            select(Notification).where(
                Notification.user_id == recipient.id,
                Notification.kind == NotificationKind.ORGANIZATION_REGISTERED,
            )
        )
        assert n is not None
        assert "Addis Tech Lab" in n.title

    # 2. Internship posting submitted for review
    posting = create_test_internship(
        db,
        org_user,
        title="AI Engineer",
        status=InternshipStatus.DRAFT,
        application_deadline=datetime.now(UTC) + timedelta(days=20),
    )
    submit_internship(db, posting.id, org_user)

    for recipient in (admin, coord):
        n = db.scalar(
            select(Notification).where(
                Notification.user_id == recipient.id,
                Notification.kind == NotificationKind.INTERNSHIP_SUBMITTED,
                Notification.title.contains("AI Engineer"),
            )
        )
        assert n is not None


def test_admin_maintains_all_coordinator_and_admin_capabilities(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Platform admin can access coordinator review and admin-only management endpoints."""
    admin = create_test_user(real_db_session, "super_admin_all@example.com", UserRole.ADMIN)
    login_test_user(real_db_client, admin.email)

    assert real_db_client.get("/api/admin/organizations").status_code == 200
    assert real_db_client.get("/api/admin/internships").status_code == 200
    assert real_db_client.get("/api/admin/users").status_code == 200
    assert real_db_client.get("/api/dashboard/admin").status_code == 200
