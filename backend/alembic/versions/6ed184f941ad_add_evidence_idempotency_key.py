"""add evidence source idempotency key

Revision ID: 6ed184f941ad
Revises: 3ab4df012e71
Create Date: 2026-11-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6ed184f941ad"
down_revision: Union[str, Sequence[str], None] = "3ab4df012e71"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "evidence",
        sa.Column("idempotency_key", sa.String(length=64), nullable=True),
    )
    op.create_index(
        "ix_evidence_idempotency_key_unique",
        "evidence",
        ["idempotency_key"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_evidence_idempotency_key_unique", table_name="evidence")
    op.drop_column("evidence", "idempotency_key")
