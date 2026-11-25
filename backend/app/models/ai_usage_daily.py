"""Daily AI call usage tracking model for per-user and global rate limits."""

from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Integer, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AiUsageDaily(Base):
    """Tracks daily AI completion calls per user and globally (user_id=None)."""

    __tablename__ = "ai_usage_daily"
    __table_args__ = (
        Index(
            "uq_ai_usage_daily_day_user",
            "day",
            "user_id",
            unique=True,
            postgresql_where=text("user_id IS NOT NULL"),
        ),
        Index(
            "uq_ai_usage_daily_day_global",
            "day",
            unique=True,
            postgresql_where=text("user_id IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    day: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    calls: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
