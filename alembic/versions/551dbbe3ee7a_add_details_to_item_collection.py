"""add details to item_collection

Revision ID: 551dbbe3ee7a
Revises: 511e8600a871
Create Date: 2016-10-18 16:31:38.527704

"""

# revision identifiers, used by Alembic.
revision = '551dbbe3ee7a'
down_revision = '511e8600a871'

from alembic import op
import sqlalchemy as sa
import coaster


def upgrade():
    op.add_column('item_collection', sa.Column('details', coaster.sqlalchemy.JsonDict(), server_default='{}', nullable=False))


def downgrade():
    op.drop_column('item_collection', 'details')
