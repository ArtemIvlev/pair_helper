"""add_announcements_table

Revision ID: add_announcements_table
Revises: 7158a0ba606e
Create Date: 2025-01-27 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_announcements_table'
down_revision = '7158a0ba606e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'announcements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('priority', sa.String(length=20), nullable=False, default='normal'),
        sa.Column('target_audience', sa.String(length=50), nullable=False, default='all'),
        sa.Column('display_settings', sa.JSON(), nullable=True, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_announcements_id'), 'announcements', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_announcements_id'), table_name='announcements')
    op.drop_table('announcements')


