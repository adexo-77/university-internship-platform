"""add approval fields to organization profiles

Revision ID: 49360543f550
Revises: e17d6f716230
Create Date: 2026-10-20 14:28:11.781653

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "49360543f550"
down_revision: str | Sequence[str] | None = "e17d6f716230"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    approval_enum = sa.Enum(
        "pending",
        "approved",
        "rejected",
        name="organization_approval_status",
    )
    approval_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "organization_profiles",
        sa.Column(
            "approval_status",
            approval_enum,
            server_default="pending",
            nullable=False,
        ),
    )
    op.add_column(
        "organization_profiles",
        sa.Column("approval_note", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "organization_profiles",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "organization_profiles",
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_organization_profiles_reviewed_by_users",
        "organization_profiles",
        "users",
        ["reviewed_by"],
        ["id"],
        ondelete="SET NULL",
    )

    # Existing organizations become approved
    op.execute(sa.text("UPDATE organization_profiles SET approval_status = 'approved'"))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_organization_profiles_reviewed_by_users",
        "organization_profiles",
        type_="foreignkey",
    )
    op.drop_column("organization_profiles", "reviewed_by")
    op.drop_column("organization_profiles", "reviewed_at")
    op.drop_column("organization_profiles", "approval_note")
    op.drop_column("organization_profiles", "approval_status")

    approval_enum = sa.Enum(
        "pending",
        "approved",
        "rejected",
        name="organization_approval_status",
    )
    approval_enum.drop(op.get_bind(), checkfirst=True)
