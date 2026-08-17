"""request fulfillment routing columns

Adds the Phase C routing columns to requests: which media-manager instance an
approved request was pushed to, its id in that manager, and the last push result.

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-17
"""
from alembic import op
import sqlalchemy as sa


revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("requests", sa.Column("target_instance_id", sa.Integer(), nullable=True))
    op.add_column("requests", sa.Column("target_service", sa.String(), nullable=True))
    op.add_column("requests", sa.Column("external_ref", sa.String(), nullable=True))
    op.add_column("requests", sa.Column("fulfillment_detail", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("requests", "fulfillment_detail")
    op.drop_column("requests", "external_ref")
    op.drop_column("requests", "target_service")
    op.drop_column("requests", "target_instance_id")
