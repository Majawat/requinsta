"""user auto-approve media types

Adds users.auto_approve_media_types (JSON list). NULL/empty => no auto-approval;
a non-empty list auto-approves that user's requests for those media types. Admins
auto-approve their own requests regardless.

Revision ID: 0010
Revises: 0009
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa


revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("auto_approve_media_types", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "auto_approve_media_types")
