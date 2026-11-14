"""persist GitHub workflow metadata

Revision ID: e7b1c3a92f10
Revises: d6d077166739
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "e7b1c3a92f10"
down_revision: Union[str, Sequence[str], None] = "d6d077166739"
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.add_column("patch_approvals", sa.Column("github_branch_sha", sa.String(length=40), nullable=True))
    op.add_column("patch_approvals", sa.Column("github_branch_url", sa.String(length=500), nullable=True))
    op.add_column("patch_approvals", sa.Column("github_pr_state", sa.String(length=30), nullable=True))

def downgrade() -> None:
    op.drop_column("patch_approvals", "github_pr_state")
    op.drop_column("patch_approvals", "github_branch_url")
    op.drop_column("patch_approvals", "github_branch_sha")
