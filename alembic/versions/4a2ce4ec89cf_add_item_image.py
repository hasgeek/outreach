"""add item_image

Revision ID: 4a2ce4ec89cf
Revises: 136d171d1022
Create Date: 2016-10-12 16:22:42.449749

"""

# revision identifiers, used by Alembic.
revision = '4a2ce4ec89cf'
down_revision = '136d171d1022'

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


def upgrade():
    op.create_table('item_image',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('url', sa.Unicode(length=2083), nullable=False),
        sa.Column('item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('primary', sa.Boolean(), nullable=True),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['item_id'], ['item.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_id', 'name'),
        sa.UniqueConstraint('item_id', 'primary')
    )
    op.create_index(op.f('item_image_item_id_fkey'), 'item_image', ['item_id'], unique=False)


def downgrade():
    op.drop_index(op.f('item_image_item_id_fkey'), table_name='item_image')
    op.drop_table('item_image')
