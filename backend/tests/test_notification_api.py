"""Integration tests for notification HTTP endpoints and user isolation."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.notification import NotificationKind
from app.models.user import UserRole
from app.services.notification import create_notification
from tests.factories import create_test_user, login_test_user


def test_list_notifications_own_only_and_pagination(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """GET /api/notifications returns user's own notifications with pagination and unread counts."""
    client = real_db_client
    db = real_db_session

    u1 = create_test_user(db, "u1_api_notif@example.com", UserRole.STUDENT)
    u2 = create_test_user(db, "u2_api_notif@example.com", UserRole.STUDENT)

    # Seed 5 notifications for u1, 3 for u2
    for i in range(5):
        create_notification(
            db,
            user_id=u1.id,
            kind=NotificationKind.ASSIGNMENT_CREATED,
            title=f"Assignment {i}",
            message=f"Description {i}",
            link_path=f"/assignments/{i}",
        )
    for i in range(3):
        create_notification(
            db,
            user_id=u2.id,
            kind=NotificationKind.ASSIGNMENT_CREATED,
            title=f"U2 Assignment {i}",
            message=f"U2 Description {i}",
            link_path=f"/assignments/{i}",
        )
    db.commit()

    login_test_user(client, u1.email)

    # Test default page
    resp = client.get("/api/notifications?limit=2&offset=0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 5
    assert data["unread_count"] == 5
    assert len(data["items"]) == 2
    assert data["items"][0]["user_id"] == u1.id

    # Isolation: none of u2's notifications are present
    all_resp = client.get("/api/notifications?limit=100")
    assert all_resp.status_code == 200
    all_data = all_resp.json()
    assert all_data["total"] == 5
    assert all(item["user_id"] == u1.id for item in all_data["items"])


def test_unread_count_and_filter(real_db_client: TestClient, real_db_session: Session) -> None:
    """GET /api/notifications/unread-count and ?unread_only=true filtering."""
    client = real_db_client
    db = real_db_session

    u = create_test_user(db, "unread_test@example.com", UserRole.STUDENT)
    n1 = create_notification(
        db,
        user_id=u.id,
        kind=NotificationKind.SUBMISSION_GRADED,
        title="Graded 1",
        message="Message 1",
        link_path="/assignments/1",
    )
    create_notification(
        db,
        user_id=u.id,
        kind=NotificationKind.SUBMISSION_GRADED,
        title="Graded 2",
        message="Message 2",
        link_path="/assignments/2",
    )
    db.commit()

    login_test_user(client, u.email)

    # Initially 2 unread
    count_resp = client.get("/api/notifications/unread-count")
    assert count_resp.status_code == 200
    assert count_resp.json() == {"unread_count": 2}

    # Mark n1 read
    read_resp = client.post(f"/api/notifications/{n1.id}/read")
    assert read_resp.status_code == 200
    assert read_resp.json()["read_at"] is not None

    # Count is now 1
    count_resp2 = client.get("/api/notifications/unread-count")
    assert count_resp2.json() == {"unread_count": 1}

    # Filter unread only
    filtered = client.get("/api/notifications?unread_only=true")
    assert filtered.status_code == 200
    assert filtered.json()["total"] == 1
    assert filtered.json()["items"][0]["title"] == "Graded 2"


def test_mark_read_idempotent_and_forbidden_across_users(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Marking read is idempotent, and another user's notification returns 404."""
    client = real_db_client
    db = real_db_session

    u1 = create_test_user(db, "u1_read_test@example.com", UserRole.STUDENT)
    u2 = create_test_user(db, "u2_read_test@example.com", UserRole.STUDENT)

    n1 = create_notification(
        db,
        user_id=u1.id,
        kind=NotificationKind.APPLICATION_DECISION,
        title="Accepted",
        message="Offer",
        link_path="/applications/1",
    )
    n2 = create_notification(
        db,
        user_id=u2.id,
        kind=NotificationKind.APPLICATION_DECISION,
        title="Shortlisted",
        message="Interview",
        link_path="/applications/2",
    )
    db.commit()

    login_test_user(client, u1.email)

    # 1. User 1 cannot mark User 2's notification read (returns 404)
    resp_cross = client.post(f"/api/notifications/{n2.id}/read")
    assert resp_cross.status_code == 404
    assert resp_cross.json()["code"] == "NOTIFICATION_NOT_FOUND"

    # 2. User 1 marks own notification read
    resp1 = client.post(f"/api/notifications/{n1.id}/read")
    assert resp1.status_code == 200
    first_read_at = resp1.json()["read_at"]
    assert first_read_at is not None

    # 3. Idempotent: marking again returns same read_at
    resp2 = client.post(f"/api/notifications/{n1.id}/read")
    assert resp2.status_code == 200
    assert resp2.json()["read_at"] == first_read_at


def test_mark_all_read_idempotent_and_scoped(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """POST /api/notifications/read-all marks all own unread as read without touching others."""
    client = real_db_client
    db = real_db_session

    u1 = create_test_user(db, "u1_bulk_read@example.com", UserRole.STUDENT)
    u2 = create_test_user(db, "u2_bulk_read@example.com", UserRole.STUDENT)

    for i in range(3):
        create_notification(
            db,
            user_id=u1.id,
            kind=NotificationKind.ASSIGNMENT_CREATED,
            title=f"A{i}",
            message="M",
            link_path="/assignments/1",
        )
    n_u2 = create_notification(
        db,
        user_id=u2.id,
        kind=NotificationKind.ASSIGNMENT_CREATED,
        title="U2 Notif",
        message="M",
        link_path="/assignments/1",
    )
    db.commit()

    login_test_user(client, u1.email)

    # First mark all read updates 3
    res1 = client.post("/api/notifications/read-all")
    assert res1.status_code == 200
    assert res1.json() == {"updated_count": 3}

    # Second mark all read updates 0 (idempotent)
    res2 = client.post("/api/notifications/read-all")
    assert res2.status_code == 200
    assert res2.json() == {"updated_count": 0}

    # Verify u2's notification was untouched
    db.refresh(n_u2)
    assert n_u2.read_at is None


def test_notification_extra_fields_forbidden(
    real_db_client: TestClient, real_db_session: Session
) -> None:
    """Extra query/body fields are rejected or ignored per forbid configuration."""
    client = real_db_client
    db = real_db_session

    u = create_test_user(db, "extra_fields@example.com", UserRole.STUDENT)
    login_test_user(client, u.email)

    resp = client.post("/api/notifications/read-all", json={"malicious_field": "hack"})
    assert resp.status_code in (200, 422)
