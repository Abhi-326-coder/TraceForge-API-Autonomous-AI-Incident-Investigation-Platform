"""Persist patch generation assumptions.

Revision ID: 8c4a91d2ef10
Revises: 6ed184f941ad
Create Date: 2026-11-18
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8c4a91d2ef10"
down_revision: Union[str, Sequence[str], None] = "6ed184f941ad"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("patch_approvals", sa.Column("assumptions", sa.JSON(), nullable=True))
    op.execute("UPDATE patch_approvals SET assumptions = '[]' WHERE assumptions IS NULL")
    op.alter_column("patch_approvals", "assumptions", existing_type=sa.JSON(), nullable=False)


def downgrade() -> None:
    op.drop_column("patch_approvals", "assumptions")
