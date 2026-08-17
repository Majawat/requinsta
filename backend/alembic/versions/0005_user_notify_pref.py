"""user notify_on_available preference

Adds users.notify_on_available (default true) so users can opt out of
availability emails.

Revision ID: 0005
Revises: 0004
Create Date: 2026-08-17
"""
from alembic import op
import sqlalchemy as sa


revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "notify_on_available",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "notify_on_available")
