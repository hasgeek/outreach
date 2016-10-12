"""add item_image

Revision ID: 5657fcc71d6c
Revises: 136d171d1022
Create Date: 2016-10-12 15:37:14.005289

"""

# revision identifiers, used by Alembic.
revision = '5657fcc71d6c'
down_revision = '136d171d1022'

import sqlalchemy_utils
from alembic import op
import sqlalchemy as sa


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
        sa.UniqueConstraint('item_id', 'name')
    )


def downgrade():
    op.drop_table('item_image')
