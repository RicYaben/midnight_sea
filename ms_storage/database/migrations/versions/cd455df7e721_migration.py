"""Migration 

Revision ID: cd455df7e721
Revises: 2c70c5dee4e6
Create Date: 2022-06-15 20:31:24.128928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd455df7e721'
down_revision = '2c70c5dee4e6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('vendor_page_id_fkey', 'vendor', type_='foreignkey')
    op.create_foreign_key(None, 'vendor', 'page', ['page_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('vendor_items_fkey', 'vendor_items', type_='foreignkey')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key('vendor_items_fkey', 'vendor_items', 'vendor', ['vendor_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    op.drop_constraint(None, 'vendor', type_='foreignkey')
    op.create_foreign_key('vendor_page_id_fkey', 'vendor', 'page', ['page_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')
    # ### end Alembic commands ###
