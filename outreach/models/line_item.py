# -*- coding: utf-8 -*-

from decimal import Decimal
import datetime
from collections import namedtuple
from sqlalchemy.sql import func
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
    __table_args__ = (db.UniqueConstraint('customer_order_id', 'seq'),)

    # seq is the relative number of the line item per order.
    seq = db.Column(db.Integer, nullable=False)
    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False, index=True, unique=False)
    order = db.relationship(Order, backref=db.backref('line_items', cascade='all, delete-orphan',
        order_by=seq,
        collection_class=ordering_list('seq', count_from=1)))

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False, index=True, unique=False)
    item = db.relationship(SaleItem, backref=db.backref('line_items', cascade='all, delete-orphan'))

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
                base_amount=item.current_price().amount if item.is_available else None))

        return line_items

    def confirm(self):
        self.status = LINE_ITEM_STATUS.CONFIRMED

    @property
    def is_confirmed(self):
        return self.status == LINE_ITEM_STATUS.CONFIRMED

    @property
    def is_cancelled(self):
        return self.status == LINE_ITEM_STATUS.CANCELLED

    def cancel(self):
        """Sets status and cancelled_at."""
        self.status = LINE_ITEM_STATUS.CANCELLED
        self.cancelled_at = func.utcnow()

    def is_cancellable(self):
        return self.is_confirmed and (datetime.datetime.now() < self.item.cancellable_until
            if self.item.cancellable_until else True)


def get_confirmed_line_items(self):
    """Returns a SQLAlchemy query object preset with an item's confirmed line items"""
    return LineItem.query.filter(LineItem.item == self, LineItem.status == LINE_ITEM_STATUS.CONFIRMED)


SaleItem.get_confirmed_line_items = property(get_confirmed_line_items)


def get_confirmed_line_items(self):
    return LineItem.query.filter(LineItem.order == self, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).all()
Order.get_confirmed_line_items = property(get_confirmed_line_items)
