"""initial

Revision ID: 0001
Revises:
Create Date: 2026-07-10 00:00:00.000000
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

message_role = postgresql.ENUM(
    "user", "assistant", name="message_role", schema="chatservice", create_type=False
)


def upgrade() -> None:
    message_role.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "chat_threads",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(_now),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(_now),
            nullable=False,
        ),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="chatservice",
    )
    op.create_index(
        "ix_chatservice_chat_threads_user_id",
        "chat_threads",
        ["user_id"],
        schema="chatservice",
    )

    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("thread_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", message_role, nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("sql", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text(_now),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["thread_id"],
            ["chatservice.chat_threads.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="chatservice",
    )
    op.create_index(
        "ix_chatservice_chat_messages_thread_id",
        "chat_messages",
        ["thread_id"],
        schema="chatservice",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_chatservice_chat_messages_thread_id",
        table_name="chat_messages",
        schema="chatservice",
    )
    op.drop_table("chat_messages", schema="chatservice")
    op.drop_index(
        "ix_chatservice_chat_threads_user_id",
        table_name="chat_threads",
        schema="chatservice",
    )
    op.drop_table("chat_threads", schema="chatservice")
    message_role.drop(op.get_bind(), checkfirst=True)
