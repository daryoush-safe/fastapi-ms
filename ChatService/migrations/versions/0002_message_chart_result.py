"""add chart spec and result payload to chat_messages

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-14 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "chat_messages",
        sa.Column("chart", postgresql.JSONB(), nullable=True),
        schema="chatservice",
    )
    op.add_column(
        "chat_messages",
        sa.Column("columns", postgresql.JSONB(), nullable=True),
        schema="chatservice",
    )
    op.add_column(
        "chat_messages",
        sa.Column("rows", postgresql.JSONB(), nullable=True),
        schema="chatservice",
    )


def downgrade() -> None:
    op.drop_column("chat_messages", "rows", schema="chatservice")
    op.drop_column("chat_messages", "columns", schema="chatservice")
    op.drop_column("chat_messages", "chart", schema="chatservice")
