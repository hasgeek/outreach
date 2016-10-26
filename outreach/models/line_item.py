# -*- coding: utf-8 -*-

from decimal import Decimal
from collections import namedtuple
from sqlalchemy.ext.orderinglist import ordering_list
from ..models import db, BaseMixin, Order, SaleItem
from coaster.utils import LabeledEnum
from baseframe import __

__all__ = ['LineItem', 'LINE_ITEM_STATUS']


class LINE_ITEM_STATUS(LabeledEnum):
    CONFIRMED = (0, __("Confirmed"))
    CANCELLED = (1, __("Cancelled"))
    PURCHASE_ORDER = (2, __("Purchase Order"))


def make_ntuple(item_id, base_amount, **kwargs):
    line_item_tup = namedtuple('LineItem', ['item_id', 'base_amount'])
    return line_item_tup(item_id,
        base_amount)


class LineItem(BaseMixin, db.Model):
    """
    Note: Line Items MUST NOT be deleted.
    They must only be cancelled.
    """
    __tablename__ = 'line_item'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('order_id', 'seq'),)

    # seq is the relative number of the line item per order.
    seq = db.Column(db.Integer, nullable=False)
    order_id = db.Column(None, db.ForeignKey('order.id'), nullable=False, index=True, unique=False)
    order = db.relationship(Order, backref=db.backref('line_items', cascade='all, delete-orphan',
        order_by=seq,
        collection_class=ordering_list('seq', count_from=1)))

    sale_item_id = db.Column(None, db.ForeignKey('sale_item.id'), nullable=False, index=True, unique=False)
    sale_item = db.relationship(SaleItem, backref=db.backref('line_items', cascade='all, delete-orphan'))

    base_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    final_amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    status = db.Column(db.Integer, default=LINE_ITEM_STATUS.PURCHASE_ORDER, nullable=False)
    ordered_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    def permissions(self, user, inherited=None):
        perms = super(LineItem, self).permissions(user, inherited)
        if self.order.organization.userid in user.organizations_owned_ids():
            perms.add('org_admin')
        return perms

    @classmethod
    def calculate(cls, line_item_dicts):
        """Returns line item tuples with the respective base_amount populated."""
        line_items = []

        # make named tuples for line items,
        # assign the base_amount for each of them, None if an item is unavailable
        for line_item_dict in line_item_dicts:
            item = SaleItem.query.get(line_item_dict['item_id'])
            line_items.append(make_ntuple(item_id=item.id,
                base_amount=item.current_price().amount if item.is_available() else None))

        return line_items

    @property
    def is_confirmed(self):
        return self.status == LINE_ITEM_STATUS.CONFIRMED

    @property
    def is_cancelled(self):
        return self.status == LINE_ITEM_STATUS.CANCELLED


def sale_item_confirmed_line_items(self):
    """Returns a SQLAlchemy query object preset with a sale item's confirmed line items"""
    return LineItem.query.filter(LineItem.sale_item == self, LineItem.status == LINE_ITEM_STATUS.CONFIRMED)


SaleItem.confirmed_line_items = property(sale_item_confirmed_line_items)


def order_confirmed_line_items(self):
    """Returns a SQLAlchemy query object preset with the order's confirmed line items"""
    return LineItem.query.filter(LineItem.order == self, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).all()
Order.confirmed_line_items = property(order_confirmed_line_items)
