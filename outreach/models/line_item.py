# -*- coding: utf-8 -*-

from decimal import Decimal
import datetime
from collections import namedtuple
from sqlalchemy.sql import func
from sqlalchemy.ext.orderinglist import ordering_list
from ..models import db, BaseMixin, Order, Item
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
    __table_args__ = (db.UniqueConstraint('customer_order_id', 'line_item_seq'),)

    # line_item_seq is the relative number of the line item per order.
    line_item_seq = db.Column(db.Integer, nullable=False)
    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False, index=True, unique=False)
    order = db.relationship(Order, backref=db.backref('line_items', cascade='all, delete-orphan',
        order_by=line_item_seq,
        collection_class=ordering_list('line_item_seq', count_from=1)))

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False, index=True, unique=False)
    item = db.relationship(Item, backref=db.backref('line_items', cascade='all, delete-orphan'))

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
            item = Item.query.get(line_item_dict['item_id'])
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


def get_availability(cls, item_ids):
    """Returns a dict -> {'item_id': ('item title', 'quantity_total', 'line_item_count')}"""
    items_dict = {}
    item_tups = db.session.query(cls.id, cls.title, cls.quantity_total, func.count(cls.id)).join(LineItem).filter(
        LineItem.item_id.in_(item_ids), LineItem.status == LINE_ITEM_STATUS.CONFIRMED).group_by(cls.id).all()
    for item_tup in item_tups:
        items_dict[unicode(item_tup[0])] = item_tup[1:]
    return items_dict


Item.get_availability = classmethod(get_availability)


def get_confirmed_line_items(self):
    """Returns a SQLAlchemy query object preset with an item's confirmed line items"""
    return LineItem.query.filter(LineItem.item == self, LineItem.status == LINE_ITEM_STATUS.CONFIRMED)


Item.get_confirmed_line_items = property(get_confirmed_line_items)


def counts_per_date_per_item(item_collection, user_tz):
    """
    Returns number of line items sold per date per item.
    Eg: {'2016-01-01': {'item-xxx': 20}}
    """
    date_item_counts = {}
    for item in item_collection.items:
        item_id = unicode(item.id)
        item_results = db.session.query('date', 'count').from_statement(
            '''SELECT DATE_TRUNC('day', line_item.ordered_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone)::date as date, count(line_item.id)
            from line_item where item_id = :item_id and status = :status group by date order by date asc'''
        ).params(timezone=user_tz, status=LINE_ITEM_STATUS.CONFIRMED, item_id=item.id)
        for res in item_results:
            if not date_item_counts.get(res[0].isoformat()):
                # if this date hasn't been been mapped in date_item_counts yet
                date_item_counts[res[0].isoformat()] = {item_id: res[1]}
            else:
                # if it has been mapped, assign the count
                date_item_counts[res[0].isoformat()][item_id] = res[1]
    return date_item_counts


def sales_by_date(dates, user_tz, item_ids):
    """
    Returns the net sales of line items sold on a date.
    Accepts a list of dates.
    ['2016-01-01', '2016-01-02'] => {'2016-01-01': }
    """
    if not item_ids:
        return None

    date_sales = {}

    for sales_date in dates:
        sales_on_date = db.session.query('sum').from_statement('''SELECT SUM(final_amount) FROM line_item
            WHERE status=:status AND DATE_TRUNC('day', line_item.ordered_at AT TIME ZONE 'UTC' AT TIME ZONE :timezone)::date = :sales_date
            AND line_item.item_id IN :item_ids
            ''').params(timezone=user_tz, status=LINE_ITEM_STATUS.CONFIRMED, sales_date=sales_date, item_ids=tuple(item_ids)).first()
        date_sales[sales_date] = sales_on_date[0] if sales_on_date[0] else Decimal(0)
    return date_sales


def sales_delta(user_tz, item_ids):
    """Calculates the percentage difference in sales between today and yesterday."""
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    sales = sales_by_date([today, yesterday], user_tz, item_ids)
    if not sales or not sales[yesterday]:
        return 0
    return round(Decimal('100') * (sales[today] - sales[yesterday])/sales[yesterday], 2)


def get_confirmed_line_items(self):
    return LineItem.query.filter(LineItem.order == self, LineItem.status == LINE_ITEM_STATUS.CONFIRMED).all()
Order.get_confirmed_line_items = property(get_confirmed_line_items)
