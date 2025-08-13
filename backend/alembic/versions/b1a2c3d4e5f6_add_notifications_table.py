"""add_notifications_table

Revision ID: b1a2c3d4e5f6
Revises: 171f376a3248
Create Date: 2025-08-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b1a2c3d4e5f6'
down_revision = '171f376a3248'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('recipient_user_id', sa.Integer(), nullable=False),
        sa.Column('pair_id', sa.Integer(), nullable=True),
        sa.Column('actor_user_id', sa.Integer(), nullable=True),
        sa.Column('entity_type', sa.String(), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['recipient_user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['pair_id'], ['pairs.id'], ),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index('ix_notifications_recipient', 'notifications', ['recipient_user_id'], unique=False)
    op.create_index('ix_notifications_pair', 'notifications', ['pair_id'], unique=False)
    op.create_index('ix_notifications_sent_at', 'notifications', ['sent_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_notifications_sent_at', table_name='notifications')
    op.drop_index('ix_notifications_pair', table_name='notifications')
    op.drop_index('ix_notifications_recipient', table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')