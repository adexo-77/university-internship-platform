"""Domain service for in-app user notifications and lifecycle events."""

from datetime import UTC, datetime
from urllib.parse import urlsplit

from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.notification import Notification, NotificationKind
from app.schemas.notification import NotificationListResponse, NotificationResponse

MAX_NOTIFICATIONS_PER_USER = 200


def prune_notifications(
    db: Session, user_id: int, max_keep: int = MAX_NOTIFICATIONS_PER_USER
) -> int:
    """Delete oldest notifications for user exceeding the max_keep limit."""
    excess_ids = list(
        db.scalars(
            select(Notification.id)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc(), Notification.id.desc())
            .offset(max_keep)
        )
    )
    if excess_ids:
        db.execute(delete(Notification).where(Notification.id.in_(excess_ids)))
        return len(excess_ids)
    return 0


def create_notification(
    db: Session,
    *,
    user_id: int,
    actor_id: int | None = None,
    kind: NotificationKind,
    title: str,
    message: str,
    link_path: str,
) -> Notification | None:
    """Create a notification in the current transaction unless actor is recipient."""
    if actor_id is not None and user_id == actor_id:
        return None

    if not link_path or not link_path.startswith("/") or link_path.startswith("//"):
        raise ValueError("link_path must start with '/' and cannot be protocol-relative")
    parsed = urlsplit(link_path)
    if parsed.scheme or parsed.netloc:
        raise ValueError("link_path must be an internal path and cannot contain scheme or host")

    notification = Notification(
        user_id=user_id,
        kind=kind,
        title=title[:120],
        message=message[:300],
        link_path=link_path[:500],
    )
    db.add(notification)
    db.flush()
    prune_notifications(db, user_id=user_id)
    return notification


def get_unread_count(db: Session, user_id: int) -> int:
    """Count unread notifications for the specified user."""
    stmt = (
        select(func.count(Notification.id))
        .where(Notification.user_id == user_id)
        .where(Notification.read_at.is_(None))
    )
    return db.scalar(stmt) or 0


def list_notifications(
    db: Session,
    user_id: int,
    unread_only: bool = False,
    limit: int = 20,
    offset: int = 0,
) -> NotificationListResponse:
    """List notifications for the authenticated user with unread count and pagination."""
    clamped_limit = min(max(limit, 1), 100)
    clamped_offset = max(offset, 0)

    count_stmt = select(func.count(Notification.id)).where(Notification.user_id == user_id)
    query_stmt = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
    )

    if unread_only:
        count_stmt = count_stmt.where(Notification.read_at.is_(None))
        query_stmt = query_stmt.where(Notification.read_at.is_(None))

    total = db.scalar(count_stmt) or 0
    unread_count = get_unread_count(db, user_id)

    items = list(db.scalars(query_stmt.offset(clamped_offset).limit(clamped_limit)))
    return NotificationListResponse(
        items=[NotificationResponse.model_validate(n) for n in items],
        total=total,
        unread_count=unread_count,
        limit=clamped_limit,
        offset=clamped_offset,
    )


def mark_notification_read(db: Session, notification_id: int, user_id: int) -> NotificationResponse:
    """Mark a single notification as read if owned by the user; otherwise raises 404."""
    notification = db.scalar(
        select(Notification).where(
            Notification.id == notification_id,
            Notification.user_id == user_id,
        )
    )
    if not notification:
        raise NotFoundException(message="Notification not found", code="NOTIFICATION_NOT_FOUND")

    if notification.read_at is None:
        notification.read_at = datetime.now(UTC)
        db.commit()
        db.refresh(notification)

    return NotificationResponse.model_validate(notification)


def mark_all_notifications_read(db: Session, user_id: int) -> int:
    """Mark all unread notifications for user as read idempotently."""
    now = datetime.now(UTC)
    stmt = (
        update(Notification)
        .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        .values(read_at=now)
    )
    result = db.execute(stmt)
    db.commit()
    return result.rowcount or 0
