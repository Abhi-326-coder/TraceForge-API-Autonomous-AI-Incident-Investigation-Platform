"""add sanitized investigation failure details

Revision ID: 3ab4df012e71
Revises: f15b27c48d2a
Create Date: 2026-11-17
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3ab4df012e71"
down_revision: Union[str, Sequence[str], None] = "f15b27c48d2a"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "investigations",
        sa.Column("failure_category", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "investigations",
        sa.Column("failure_message", sa.Text(), nullable=True),
    )
    op.add_column(
        "investigations",
        sa.Column("failure_is_terminal", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("investigations", "failure_is_terminal")
    op.drop_column("investigations", "failure_message")
    op.drop_column("investigations", "failure_category")
