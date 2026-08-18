"""media manager monitor scope

Adds media_manager_instances.monitor_scope: how much to monitor when a request
is pushed to the manager. "item" = only the requested book/album (default);
"collection" = the whole author/artist. Maps to the arr author/artist
addOptions.monitor ("none" vs "all").

server_default="item" backfills existing rows, so a request stops monitoring an
author's entire catalogue by default (the previous behaviour).

Revision ID: 0008
Revises: 0007
Create Date: 2026-08-18
"""
from alembic import op
import sqlalchemy as sa


revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "media_manager_instances",
        sa.Column("monitor_scope", sa.String(), nullable=False, server_default="item"),
    )


def downgrade() -> None:
    op.drop_column("media_manager_instances", "monitor_scope")
