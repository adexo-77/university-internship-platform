"""add_preferred_work_modes_and_preferred_location_to_student_profiles

Revision ID: 04aa253deb9b
Revises: 4486e293b423
Create Date: 2026-10-28 10:27:21.262415

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "04aa253deb9b"
down_revision: str | Sequence[str] | None = "4486e293b423"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "student_profiles",
        sa.Column(
            "preferred_work_modes",
            sa.ARRAY(sa.String(length=20)),
            nullable=False,
            server_default="{}",
        ),
    )
    op.add_column(
        "student_profiles",
        sa.Column("preferred_location", sa.String(length=80), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("student_profiles", "preferred_location")
    op.drop_column("student_profiles", "preferred_work_modes")
