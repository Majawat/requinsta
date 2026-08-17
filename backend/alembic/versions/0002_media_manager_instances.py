"""media manager instances

Adds the media_manager_instances table (Phase B): configured downstream
media managers (Readarr/Radarr/Sonarr/Lidarr and Readarr-API-compatible forks)
that approved requests can be routed to.

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-17
"""
from alembic import op
import sqlalchemy as sa


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "media_manager_instances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("base_url", sa.String(), nullable=False),
        sa.Column("api_key", sa.String(), nullable=True),
        sa.Column("media_types", sa.JSON(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("root_folder_path", sa.String(), nullable=True),
        sa.Column("quality_profile_id", sa.Integer(), nullable=True),
        sa.Column("metadata_profile_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_media_manager_instances_id",
        "media_manager_instances",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_media_manager_instances_id", table_name="media_manager_instances"
    )
    op.drop_table("media_manager_instances")
