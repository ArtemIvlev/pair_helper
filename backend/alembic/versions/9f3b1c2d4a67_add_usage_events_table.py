"""add_usage_events_table

Revision ID: 9f3b1c2d4a67
Revises: 171f376a3248
Create Date: 2025-08-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9f3b1c2d4a67'
down_revision = '171f376a3248'
branch_labels = None
depends_on = None


def upgrade() -> None:
	op.create_table(
		"usage_events",
		sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
		sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
		sa.Column("method", sa.String(length=16), nullable=False),
		sa.Column("route", sa.String(length=512), nullable=False),
		sa.Column("status", sa.Integer(), nullable=False),
		sa.Column("duration_ms", sa.Integer(), nullable=False),
		sa.Column("telegram_id", sa.BigInteger(), nullable=True),
	)
	op.create_index(op.f('ix_usage_events_id'), 'usage_events', ['id'], unique=False)
	op.create_index('ix_usage_events_ts', 'usage_events', ['ts'], unique=False)
	op.create_index('ix_usage_events_route', 'usage_events', ['route'], unique=False)
	op.create_index('ix_usage_events_telegram_id', 'usage_events', ['telegram_id'], unique=False)


def downgrade() -> None:
	op.drop_index('ix_usage_events_telegram_id', table_name='usage_events')
	op.drop_index('ix_usage_events_route', table_name='usage_events')
	op.drop_index('ix_usage_events_ts', table_name='usage_events')
	op.drop_index(op.f('ix_usage_events_id'), table_name='usage_events')
	op.drop_table('usage_events')


