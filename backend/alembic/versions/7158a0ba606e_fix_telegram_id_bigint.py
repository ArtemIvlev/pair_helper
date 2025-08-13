"""fix_telegram_id_bigint

Revision ID: 7158a0ba606e
Revises: 171f376a3248
Create Date: 2025-08-13 10:24:27.565233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7158a0ba606e'
down_revision = '171f376a3248'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Изменяем тип telegram_id с INTEGER на BIGINT
    op.alter_column('users', 'telegram_id',
                    existing_type=sa.INTEGER(),
                    type_=sa.BIGINT(),
                    existing_nullable=False)


def downgrade() -> None:
    # Возвращаем тип telegram_id обратно на INTEGER
    op.alter_column('users', 'telegram_id',
                    existing_type=sa.BIGINT(),
                    type_=sa.INTEGER(),
                    existing_nullable=False)
