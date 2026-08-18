"""add podcast media type

Adds 'PODCAST' to the mediatype enum. The DB stores the enum member *name*
(uppercase), while the API accepts/returns the lowercase value ("podcast").
No media-manager / metadata mapping yet — a podcast request is a manual request
for now.

Revision ID: 0007
Revises: 0006
Create Date: 2026-08-18
"""
from alembic import op


revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres 12+ allows ADD VALUE inside a transaction as long as the new value
    # isn't used in the same transaction (it isn't here). Idempotent so a re-run
    # is safe.
    op.execute("ALTER TYPE mediatype ADD VALUE IF NOT EXISTS 'PODCAST'")


def downgrade() -> None:
    # Postgres cannot drop a single enum value. Removing it would require
    # recreating the type and rewriting the column; not worth it for a downgrade.
    # No-op (leaving the value in place is harmless).
    pass
