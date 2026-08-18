"""issues table

Adds the issues table: problems users report on fulfilled media.

Revision ID: 0006
Revises: 0005
Create Date: 2026-08-17
"""
from alembic import op
import sqlalchemy as sa


revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "issues",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "WRONG_CONTENT", "QUALITY", "PLAYBACK", "INCOMPLETE", "OTHER",
                name="issuecategory",
            ),
            nullable=False,
        ),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("OPEN", "RESOLVED", name="issuestatus"),
            nullable=False,
        ),
        sa.Column("admin_response", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["request_id"], ["requests.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_issues_id", "issues", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_issues_id", table_name="issues")
    op.drop_table("issues")
    sa.Enum(name="issuestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="issuecategory").drop(op.get_bind(), checkfirst=True)
