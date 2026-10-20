"""add review fields and statuses to internship postings

Revision ID: c4d9a28e57f1
Revises: 49360543f550
Create Date: 2026-10-20 19:20:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4d9a28e57f1"
down_revision: str | Sequence[str] | None = "49360543f550"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute(
                sa.text(
                    "ALTER TYPE internship_status "
                    "ADD VALUE IF NOT EXISTS 'pending_review' BEFORE 'open'"
                )
            )
            op.execute(
                sa.text(
                    "ALTER TYPE internship_status "
                    "ADD VALUE IF NOT EXISTS 'rejected' BEFORE 'closed'"
                )
            )

    op.add_column(
        "internship_postings",
        sa.Column("review_note", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "internship_postings",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "internship_postings",
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_internship_postings_reviewed_by_users",
        "internship_postings",
        "users",
        ["reviewed_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_internship_postings_reviewed_by_users",
        "internship_postings",
        type_="foreignkey",
    )
    op.drop_column("internship_postings", "reviewed_by")
    op.drop_column("internship_postings", "reviewed_at")
    op.drop_column("internship_postings", "review_note")
