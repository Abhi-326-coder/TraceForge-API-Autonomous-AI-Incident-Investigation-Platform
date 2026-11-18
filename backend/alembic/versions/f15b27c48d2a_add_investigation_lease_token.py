"""add unique investigation lease token

Revision ID: f15b27c48d2a
Revises: e7b1c3a92f10
Create Date: 2026-11-17

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f15b27c48d2a"
down_revision: Union[str, Sequence[str], None] = "e7b1c3a92f10"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "investigations",
        sa.Column("lease_token", sa.Uuid(as_uuid=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("investigations", "lease_token")
