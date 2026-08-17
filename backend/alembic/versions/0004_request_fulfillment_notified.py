"""request fulfillment_notified flag

Adds requests.fulfillment_notified (Phase D) so a fulfilled request is only
notified once even if its status is toggled through FULFILLED again.

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-17
"""
from alembic import op
import sqlalchemy as sa


revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "requests",
        sa.Column(
            "fulfillment_notified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("requests", "fulfillment_notified")
