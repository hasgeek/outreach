from flask_admin.contrib.sqla import ModelView
from . import lastuser
from flask_admin.form.fields import JSONField


class SiteAdminModelView(ModelView):
    def is_accessible(self):
        return lastuser.has_permission('siteadmin')


class OrganizationModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_list = ('id', 'title')
    form_list = ('id', 'userid', 'title')
    form_excluded_columns = ['userid', 'item_collections', 'orders', 'created_at', 'updated_at']
    form_overrides = dict(details=JSONField)


class OrderModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['item_collection']
    column_list = ('id', 'buyer_email', 'buyer_fullname', 'buyer_phone', 'status')
    form_excluded_columns = ['parent', 'items', 'orders', 'categories', 'created_at', 'updated_at']


class ItemCollectionModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['organization']
    column_list = ('id', 'title')
    form_excluded_columns = ['parent', 'items', 'orders', 'categories', 'created_at', 'updated_at']
    form_overrides = dict(details=JSONField)


class CategoryModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['item_collection']
    column_list = ('id', 'title')
    form_excluded_columns = ['parent', 'items', 'created_at', 'updated_at']


class InventoryItemModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['item_collection']
    column_searchable_list = ['title']
    column_list = ('id', 'title')
    form_excluded_columns = ['parent', 'line_items', 'created_at', 'updated_at']


class SaleItemModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['item_collection']
    column_searchable_list = ['title']
    column_list = ('id', 'title')
    form_excluded_columns = ['parent', 'line_items', 'created_at', 'updated_at']


class SaleItemImageView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['sale_item']
    column_list = ('sale_item', 'url')
    form_excluded_columns = ['parent', 'created_at', 'updated_at']


class PriceModelView(SiteAdminModelView):
    can_delete = False
    column_display_pk = True
    column_filters = ['sale_item']
    column_list = ('id', 'sale_item', 'title', 'start_at', 'end_at', 'currency', 'amount')
    form_excluded_columns = ['parent', 'created_at', 'updated_at']
