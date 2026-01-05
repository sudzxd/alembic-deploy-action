"""Dangerous migration example

Revision ID: 003
Revises: 002
Create Date: 2025-01-05

"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column('users', 'email')
    op.add_column('posts', sa.Column('published', sa.Boolean(), default=False))


def downgrade() -> None:
    op.drop_column('posts', 'published')
    op.add_column('users', sa.Column('email', sa.String(length=100), nullable=False))
