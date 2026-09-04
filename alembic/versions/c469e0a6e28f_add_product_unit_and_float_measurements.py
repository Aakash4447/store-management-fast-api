"""add product unit and float measurements

Revision ID: c469e0a6e28f
Revises: bafaf3abda51
Create Date: 2026-09-04 21:29:41.525212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c469e0a6e28f'
down_revision: Union[str, None] = 'bafaf3abda51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


product_unit_enum = sa.Enum('KG', 'G', 'L', 'ML', name='product_unit')


def upgrade() -> None:
    op.alter_column('order_items', 'quantity',
               existing_type=sa.INTEGER(),
               type_=sa.Numeric(precision=10, scale=3),
               existing_nullable=False)

    # Existing products have no unit yet, so backfill 'kg' before requiring it going forward.
    product_unit_enum.create(op.get_bind(), checkfirst=True)
    op.add_column('products', sa.Column('unit', product_unit_enum, nullable=False, server_default='KG'))
    op.alter_column('products', 'unit', server_default=None)

    op.alter_column('products', 'stock_quantity',
               existing_type=sa.INTEGER(),
               type_=sa.Numeric(precision=10, scale=3),
               existing_nullable=False)


def downgrade() -> None:
    op.alter_column('products', 'stock_quantity',
               existing_type=sa.Numeric(precision=10, scale=3),
               type_=sa.INTEGER(),
               existing_nullable=False)
    op.drop_column('products', 'unit')
    product_unit_enum.drop(op.get_bind(), checkfirst=True)
    op.alter_column('order_items', 'quantity',
               existing_type=sa.Numeric(precision=10, scale=3),
               type_=sa.INTEGER(),
               existing_nullable=False)
