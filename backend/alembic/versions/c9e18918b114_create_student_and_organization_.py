"""create student and organization profiles tables

Revision ID: c9e18918b114
Revises: 6d7757d439a5
Create Date: 2026-10-18 08:57:51.215432

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9e18918b114"
down_revision: str | Sequence[str] | None = "6d7757d439a5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("university", sa.String(length=255), nullable=True),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("year_of_study", sa.Integer(), nullable=True),
        sa.Column("bio", sa.String(length=1000), nullable=True),
        sa.Column(
            "skills",
            sa.ARRAY(sa.String(length=40)),
            server_default=sa.text("'{}'::text[]"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "year_of_study IS NULL OR (year_of_study >= 1 AND year_of_study <= 6)",
            name="check_student_year_of_study",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_student_profiles_user_id"),
    )
    op.create_index(
        op.f("ix_student_profiles_user_id"),
        "student_profiles",
        ["user_id"],
        unique=True,
    )

    op.create_table(
        "organization_profiles",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_name", sa.String(length=255), nullable=False),
        sa.Column("industry", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_organization_profiles_user_id"),
    )
    op.create_index(
        op.f("ix_organization_profiles_user_id"),
        "organization_profiles",
        ["user_id"],
        unique=True,
    )

    # Backfill missing profile rows for existing student and organization users
    op.execute(
        sa.text(
            """
            INSERT INTO student_profiles (user_id, skills, updated_at)
            SELECT u.id, '{}'::text[], now()
            FROM users u
            WHERE u.role = 'student'
              AND NOT EXISTS (
                  SELECT 1 FROM student_profiles sp WHERE sp.user_id = u.id
              );
            """
        )
    )
    op.execute(
        sa.text(
            """
            INSERT INTO organization_profiles (user_id, organization_name, updated_at)
            SELECT u.id, u.full_name, now()
            FROM users u
            WHERE u.role = 'organization'
              AND NOT EXISTS (
                  SELECT 1 FROM organization_profiles op WHERE op.user_id = u.id
              );
            """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_organization_profiles_user_id"),
        table_name="organization_profiles",
    )
    op.drop_table("organization_profiles")
    op.drop_index(
        op.f("ix_student_profiles_user_id"),
        table_name="student_profiles",
    )
    op.drop_table("student_profiles")
