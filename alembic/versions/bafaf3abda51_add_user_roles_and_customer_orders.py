"""add user roles and customer orders

Revision ID: bafaf3abda51
Revises: ddbb872beab8
Create Date: 2026-09-04 20:35:01.072000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'bafaf3abda51'
down_revision: Union[str, None] = 'ddbb872beab8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

user_role_enum = sa.Enum('ADMIN', 'STORE_OWNER', 'CUSTOMER', name='user_role')


def upgrade() -> None:
    # store_owners -> users: rename in place (rather than drop/create) to preserve existing accounts.
    op.rename_table('store_owners', 'users')
    op.execute(sa.text("ALTER INDEX ix_store_owners_email RENAME TO ix_users_email"))

    user_role_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'users',
        sa.Column('role', user_role_enum, nullable=False, server_default='STORE_OWNER'),
    )
    op.alter_column('users', 'role', server_default=None)

    # orders table has no existing rows yet in any deployed environment for this app, so
    # customer_id can be added as NOT NULL directly without a backfill step.
    op.add_column('orders', sa.Column('customer_id', sa.UUID(), nullable=False))
    op.create_index(op.f('ix_orders_customer_id'), 'orders', ['customer_id'], unique=False)
    op.create_foreign_key(
        'orders_customer_id_fkey', 'orders', 'users', ['customer_id'], ['id'], ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('orders_customer_id_fkey', 'orders', type_='foreignkey')
    op.drop_index(op.f('ix_orders_customer_id'), table_name='orders')
    op.drop_column('orders', 'customer_id')

    op.drop_column('users', 'role')
    user_role_enum.drop(op.get_bind(), checkfirst=True)

    op.execute(sa.text("ALTER INDEX ix_users_email RENAME TO ix_store_owners_email"))
    op.rename_table('users', 'store_owners')
