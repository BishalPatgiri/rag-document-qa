"""add query_logs table

Revision ID: 0002
Revises: 0001
Create Date: 2026-06-23

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "query_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("mode", sa.String(length=16), nullable=False),
        sa.Column("retrieved_chunk_ids", sa.JSON(), nullable=True),
        sa.Column("latency_ms", sa.Float(), nullable=False, server_default="0"),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "completion_tokens", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "embedding_tokens", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("est_cost_usd", sa.Float(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_query_logs_created_at", "query_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_query_logs_created_at", table_name="query_logs")
    op.drop_table("query_logs")
