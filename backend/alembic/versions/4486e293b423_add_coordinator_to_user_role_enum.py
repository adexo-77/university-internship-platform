"""add coordinator to user role enum

Revision ID: 4486e293b423
Revises: f5b72183c0aa
Create Date: 2026-10-25 20:32:23.346763

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4486e293b423"
down_revision: str | Sequence[str] | None = "f5b72183c0aa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.get_context().autocommit_block():
        op.execute(sa.text("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'coordinator'"))


def downgrade() -> None:
    """Downgrade schema."""
    pass
