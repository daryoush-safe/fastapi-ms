"""initial

Revision ID: 0001
Revises:
Create Date: 2026-05-08 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
default_created_at: str = "now()"


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS auth")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(default_created_at),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(default_created_at),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="auth",
    )
    op.create_index(
        "ix_auth_users_email", "users", ["email"], unique=True, schema="auth"
    )

    op.create_table(
        "outbox",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("aggregate_id", sa.String(), nullable=False),
        sa.Column("aggregate_type", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "processed", "failed", name="outboxstatus", schema="auth"
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(default_created_at),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="auth",
    )
    op.create_index(
        "ix_outbox_status_created_at",
        "outbox",
        ["status", "created_at"],
        schema="auth",
    )


def downgrade() -> None:
    op.drop_index("ix_outbox_status_created_at", table_name="outbox", schema="auth")
    op.drop_table("outbox", schema="auth")
    op.drop_index("ix_auth_users_email", table_name="users", schema="auth")
    op.drop_table("users", schema="auth")
    op.execute("DROP TYPE IF EXISTS auth.outboxstatus")
    op.execute("DROP SCHEMA IF EXISTS auth")
