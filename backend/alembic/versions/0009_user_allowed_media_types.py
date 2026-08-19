"""user allowed media types

Adds users.allowed_media_types (JSON list). NULL/empty = unrestricted (all types);
a non-empty list restricts the user to those media types for search + requests.
Admins are never restricted. Existing users default to NULL (unrestricted).

Revision ID: 0009
Revises: 0008
Create Date: 2026-08-18
"""
from alembic import op
import sqlalchemy as sa


revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("allowed_media_types", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "allowed_media_types")
