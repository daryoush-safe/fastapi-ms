"""initial

Revision ID: 0001
Revises:
Create Date: 2026-06-12 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_now = "now()"


def upgrade() -> None:
    op.create_table(
        "connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("engine", sa.String(50), nullable=False),
        sa.Column("dsn", sa.Text(), nullable=False),
        sa.Column("schema_cache", postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(_now),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="dbservice",
    )
    op.create_index(
        "ix_dbservice_connections_owner_id",
        "connections",
        ["owner_id"],
        schema="dbservice",
    )

    op.create_table(
        "queries_outbox",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("aggregate_id", sa.String(), nullable=False),
        sa.Column("aggregate_type", sa.String(), nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "processed", "failed",
                name="outboxstatus_db",
                schema="dbservice",
            ),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(_now),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="dbservice",
    )
    op.create_index(
        "ix_db_outbox_status_created_at",
        "queries_outbox",
        ["status", "created_at"],
        schema="dbservice",
    )

    op.execute(
        "CREATE PUBLICATION dbz_publication_db FOR TABLE dbservice.queries_outbox"
    )


def downgrade() -> None:
    op.execute("DROP PUBLICATION IF EXISTS dbz_publication_db")
    op.drop_index("ix_db_outbox_status_created_at", table_name="queries_outbox", schema="dbservice")
    op.drop_table("queries_outbox", schema="dbservice")
    op.execute("DROP TYPE IF EXISTS dbservice.outboxstatus_db")
    op.drop_index("ix_dbservice_connections_owner_id", table_name="connections", schema="dbservice")
    op.drop_table("connections", schema="dbservice")
