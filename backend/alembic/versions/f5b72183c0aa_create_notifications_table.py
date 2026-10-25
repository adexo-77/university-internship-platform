"""create notifications table and pruning trigger

Revision ID: f5b72183c0aa
Revises: cbd29ec4559d
Create Date: 2026-10-25 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f5b72183c0aa"
down_revision: str | Sequence[str] | None = "cbd29ec4559d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "kind",
            sa.Enum(
                "submission_graded",
                "application_decision",
                "assignment_created",
                "first_submission",
                "application_received",
                "internship_status",
                "organization_status",
                "organization_registered",
                "internship_submitted",
                "password_reset",
                name="notification_kind",
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("message", sa.String(length=300), nullable=False),
        sa.Column("link_path", sa.String(length=500), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "link_path LIKE '/%' AND link_path NOT LIKE '//%' AND link_path NOT LIKE '%://%'",
            name="ck_notifications_link_path_internal",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notifications_user_id"),
        "notifications",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_notifications_user_read_created",
        "notifications",
        ["user_id", "read_at", "created_at"],
        unique=False,
    )
    op.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION prune_user_notifications()
            RETURNS TRIGGER AS $$
            BEGIN
                DELETE FROM notifications
                WHERE id IN (
                    SELECT id FROM notifications
                    WHERE user_id = NEW.user_id
                    ORDER BY created_at DESC, id DESC
                    OFFSET 200
                );
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS tr_prune_notifications ON notifications;
            CREATE TRIGGER tr_prune_notifications
            AFTER INSERT ON notifications
            FOR EACH ROW
            EXECUTE FUNCTION prune_user_notifications();
            """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        sa.text(
            """
            DROP TRIGGER IF EXISTS tr_prune_notifications ON notifications;
            DROP FUNCTION IF EXISTS prune_user_notifications();
            """
        )
    )
    op.drop_index("ix_notifications_user_read_created", table_name="notifications")
    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_table("notifications")
    sa.Enum(name="notification_kind").drop(op.get_bind(), checkfirst=True)
