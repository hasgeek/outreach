"""init models

Revision ID: 511e8600a871
Revises: None
Create Date: 2016-10-14 21:38:36.064720

"""

# revision identifiers, used by Alembic.
revision = '511e8600a871'
down_revision = None

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
import coaster


def upgrade():
    op.create_table('organization',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('details', coaster.sqlalchemy.JsonDict(), server_default='{}', nullable=False),
        sa.Column('contact_email', sa.Unicode(length=254), nullable=False),
        sa.Column('userid', sa.Unicode(length=22), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_email'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('userid')
    )
    op.create_table('user',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('userid', sa.String(length=22), nullable=False),
        sa.Column('lastuser_token_scope', sa.Unicode(length=250), nullable=True),
        sa.Column('lastuser_token_type', sa.Unicode(length=250), nullable=True),
        sa.Column('userinfo', coaster.sqlalchemy.JsonDict(), nullable=True),
        sa.Column('email', sa.Unicode(length=80), nullable=True),
        sa.Column('lastuser_token', sa.String(length=22), nullable=True),
        sa.Column('username', sa.Unicode(length=80), nullable=True),
        sa.Column('fullname', sa.Unicode(length=80), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('lastuser_token'),
        sa.UniqueConstraint('userid'),
        sa.UniqueConstraint('username')
    )
    op.create_table('inventory_item',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('quantity_total', sa.Integer(), nullable=False),
        sa.Column('cancellable_until', sa.DateTime(), nullable=True),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('item_collection',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('description_text', sa.UnicodeText(), nullable=False),
        sa.Column('description_html', sa.UnicodeText(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('organization_id', 'name')
    )
    op.create_table('category',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('item_collection_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('seq', sa.Integer(), nullable=False),
        sa.Column('description_text', sa.UnicodeText(), nullable=False),
        sa.Column('description_html', sa.UnicodeText(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['item_collection_id'], ['item_collection.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('item_collection_id', 'name'),
        sa.UniqueConstraint('item_collection_id', 'seq')
    )
    op.create_table('customer_order',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('item_collection_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('initiated_at', sa.DateTime(), nullable=False),
        sa.Column('inquired_at', sa.DateTime(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('invoiced_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('access_token', sa.Unicode(length=22), nullable=False),
        sa.Column('buyer_email', sa.Unicode(length=254), nullable=False),
        sa.Column('buyer_fullname', sa.Unicode(length=80), nullable=False),
        sa.Column('buyer_phone', sa.Unicode(), nullable=False),
        sa.Column('buyer_company', sa.Unicode(length=80), nullable=True),
        sa.Column('invoice_no', sa.Integer(), nullable=True),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['item_collection_id'], ['item_collection.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('access_token'),
        sa.UniqueConstraint('organization_id', 'invoice_no')
    )
    op.create_table('order_session',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('customer_order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('referrer', sa.Unicode(length=2083), nullable=True),
        sa.Column('utm_source', sa.Unicode(length=250), nullable=False),
        sa.Column('utm_medium', sa.Unicode(length=250), nullable=False),
        sa.Column('utm_term', sa.Unicode(length=250), nullable=False),
        sa.Column('utm_content', sa.Unicode(length=250), nullable=False),
        sa.Column('utm_id', sa.Unicode(length=250), nullable=False),
        sa.Column('utm_campaign', sa.Unicode(length=250), nullable=False),
        sa.Column('gclid', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['customer_order_id'], ['customer_order.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_session_customer_order_id'), 'order_session', ['customer_order_id'], unique=False)
    op.create_index(op.f('ix_order_session_gclid'), 'order_session', ['gclid'], unique=False)
    op.create_index(op.f('ix_order_session_utm_campaign'), 'order_session', ['utm_campaign'], unique=False)
    op.create_index(op.f('ix_order_session_utm_id'), 'order_session', ['utm_id'], unique=False)
    op.create_index(op.f('ix_order_session_utm_medium'), 'order_session', ['utm_medium'], unique=False)
    op.create_index(op.f('ix_order_session_utm_source'), 'order_session', ['utm_source'], unique=False)
    op.create_table('sale_item',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('item_collection_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('description_text', sa.UnicodeText(), nullable=False),
        sa.Column('description_html', sa.UnicodeText(), nullable=False),
        sa.Column('seq', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
        sa.ForeignKeyConstraint(['item_collection_id'], ['item_collection.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('inventory_item_sale_item',
        sa.Column('inventory_item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('sale_item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['inventory_item.id'], ),
        sa.ForeignKeyConstraint(['sale_item_id'], ['sale_item.id'], ),
        sa.PrimaryKeyConstraint('inventory_item_id', 'sale_item_id')
    )
    op.create_table('line_item',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('seq', sa.Integer(), nullable=False),
        sa.Column('customer_order_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('sale_item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('base_amount', sa.Numeric(), nullable=False),
        sa.Column('final_amount', sa.Numeric(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('ordered_at', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['customer_order_id'], ['customer_order.id'], ),
        sa.ForeignKeyConstraint(['sale_item_id'], ['sale_item.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('customer_order_id', 'seq')
    )
    op.create_index(op.f('ix_line_item_customer_order_id'), 'line_item', ['customer_order_id'], unique=False)
    op.create_index(op.f('ix_line_item_sale_item_id'), 'line_item', ['sale_item_id'], unique=False)
    op.create_table('price',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('sale_item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('start_at', sa.DateTime(), nullable=False),
        sa.Column('end_at', sa.DateTime(), nullable=False),
        sa.Column('amount', sa.Numeric(), nullable=False),
        sa.Column('currency', sa.Unicode(length=3), nullable=False),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.CheckConstraint(u'start_at < end_at', name='price_start_at_lt_end_at_check'),
        sa.ForeignKeyConstraint(['sale_item_id'], ['sale_item.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sale_item_id', 'name')
    )
    op.create_table('sale_item_image',
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('url', sa.Unicode(length=2083), nullable=False),
        sa.Column('sale_item_id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column('primary', sa.Boolean(), nullable=True),
        sa.Column('name', sa.Unicode(length=250), nullable=False),
        sa.Column('title', sa.Unicode(length=250), nullable=False),
        sa.Column('id', sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.ForeignKeyConstraint(['sale_item_id'], ['sale_item.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sale_item_id', 'name'),
        sa.UniqueConstraint('sale_item_id', 'primary')
    )
    op.create_index(op.f('ix_sale_item_image_sale_item_id'), 'sale_item_image', ['sale_item_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_sale_item_image_sale_item_id'), table_name='sale_item_image')
    op.drop_table('sale_item_image')
    op.drop_table('price')
    op.drop_index(op.f('ix_line_item_sale_item_id'), table_name='line_item')
    op.drop_index(op.f('ix_line_item_customer_order_id'), table_name='line_item')
    op.drop_table('line_item')
    op.drop_table('inventory_item_sale_item')
    op.drop_table('sale_item')
    op.drop_index(op.f('ix_order_session_utm_source'), table_name='order_session')
    op.drop_index(op.f('ix_order_session_utm_medium'), table_name='order_session')
    op.drop_index(op.f('ix_order_session_utm_id'), table_name='order_session')
    op.drop_index(op.f('ix_order_session_utm_campaign'), table_name='order_session')
    op.drop_index(op.f('ix_order_session_gclid'), table_name='order_session')
    op.drop_index(op.f('ix_order_session_customer_order_id'), table_name='order_session')
    op.drop_table('order_session')
    op.drop_table('customer_order')
    op.drop_table('category')
    op.drop_table('item_collection')
    op.drop_table('inventory_item')
    op.drop_table('user')
    op.drop_table('organization')
