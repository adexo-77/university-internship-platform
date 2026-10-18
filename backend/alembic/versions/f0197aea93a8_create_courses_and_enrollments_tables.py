"""create courses and enrollments tables

Revision ID: f0197aea93a8
Revises: c9e18918b114
Create Date: 2026-10-18 10:42:43.081703

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f0197aea93a8"
down_revision: str | Sequence[str] | None = "c9e18918b114"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "courses",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("instructor_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=True),
        sa.Column(
            "status",
            sa.Enum("draft", "published", name="course_status"),
            server_default="draft",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["instructor_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_courses_instructor_id"), "courses", ["instructor_id"], unique=False)
    op.create_table(
        "enrollments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column(
            "enrolled_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", "student_id", name="uq_enrollments_course_student"),
    )
    op.create_index(op.f("ix_enrollments_student_id"), "enrollments", ["student_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_enrollments_student_id"), table_name="enrollments")
    op.drop_table("enrollments")
    op.drop_index(op.f("ix_courses_instructor_id"), table_name="courses")
    op.drop_table("courses")
    sa.Enum("draft", "published", name="course_status").drop(op.get_bind(), checkfirst=True)
