"""Tests for pruning limits, link path validation, and transaction atomicity."""

import pytest
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.notification import Notification, NotificationKind
from app.models.user import UserRole
from app.services.notification import (
    MAX_NOTIFICATIONS_PER_USER,
    create_notification,
    prune_notifications,
)
from tests.factories import create_test_user


def test_200_limit_prunes_oldest_notifications(real_db_session: Session) -> None:
    """A user cannot exceed 200 notifications; older notifications are pruned on insert."""
    db = real_db_session
    user = create_test_user(db, "prune_test_user@example.com", UserRole.STUDENT)

    # Insert 205 notifications
    for i in range(205):
        create_notification(
            db,
            user_id=user.id,
            kind=NotificationKind.ASSIGNMENT_CREATED,
            title=f"Notification #{i}",
            message=f"Message #{i}",
            link_path=f"/assignments/{i}",
        )
    db.commit()

    total_count = db.scalar(
        select(func.count(Notification.id)).where(Notification.user_id == user.id)
    )
    assert total_count == MAX_NOTIFICATIONS_PER_USER

    # Verify that the 5 oldest (indices 0..4) are pruned and indices 5..204 remain
    remaining_titles = set(
        db.scalars(select(Notification.title).where(Notification.user_id == user.id))
    )
    for i in range(5):
        assert f"Notification #{i}" not in remaining_titles
    for i in range(5, 205):
        assert f"Notification #{i}" in remaining_titles


def test_prune_notifications_manual_call_idempotent(real_db_session: Session) -> None:
    """Calling prune_notifications when under or at limit deletes 0 items."""
    db = real_db_session
    user = create_test_user(db, "manual_prune_user@example.com", UserRole.STUDENT)
    for i in range(10):
        create_notification(
            db,
            user_id=user.id,
            kind=NotificationKind.ASSIGNMENT_CREATED,
            title=f"Note {i}",
            message="Msg",
            link_path="/assignments/1",
        )
    db.commit()

    pruned = prune_notifications(db, user.id, max_keep=200)
    assert pruned == 0


def test_link_path_validation_rejects_external_schemes_and_hosts(
    real_db_session: Session,
) -> None:
    """link_path must start with '/' and never contain scheme or host."""
    db = real_db_session
    user = create_test_user(db, "link_val_user@example.com", UserRole.STUDENT)

    invalid_links = [
        "https://evil.com/hack",
        "http://attacker.org",
        "//protocol-relative.com/path",
        "javascript:alert(1)",
        "data:text/html,hack",
        "relative/path/without/slash",
        "",
    ]

    for bad_link in invalid_links:
        with pytest.raises(ValueError, match="link_path must"):
            create_notification(
                db,
                user_id=user.id,
                kind=NotificationKind.PASSWORD_RESET,
                title="Bad Link",
                message="Message",
                link_path=bad_link,
            )

    valid_links = [
        "/assignments/42",
        "/internships/15",
        "/profile",
        "/admin/organizations",
        "/my-applications",
    ]
    for good_link in valid_links:
        n = create_notification(
            db,
            user_id=user.id,
            kind=NotificationKind.PASSWORD_RESET,
            title="Good Link",
            message="Message",
            link_path=good_link,
        )
        assert n is not None
        assert n.link_path == good_link


def test_failing_event_leaves_no_orphan_notification(real_db_session: Session) -> None:
    """An event failure rolling back the database session leaves no orphan notification."""
    db = real_db_session
    user = create_test_user(db, "rollback_user@example.com", UserRole.STUDENT)

    try:
        create_notification(
            db,
            user_id=user.id,
            kind=NotificationKind.SUBMISSION_GRADED,
            title="Orphan Test",
            message="Should be rolled back",
            link_path="/assignments/1",
        )
        raise RuntimeError("Simulated transaction failure")
    except RuntimeError:
        db.rollback()

    orphan = db.scalar(
        select(Notification).where(
            Notification.user_id == user.id,
            Notification.title == "Orphan Test",
        )
    )
    assert orphan is None
