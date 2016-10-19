# -*- coding: utf-8 -*-

from decimal import Decimal
from datetime import datetime
from collections import namedtuple
from sqlalchemy import sql
from ..models import db, BaseMixin, User
from coaster.utils import LabeledEnum, buid
from baseframe import __

__all__ = ['Order', 'ORDER_STATUS', 'OrderSession']


class ORDER_STATUS(LabeledEnum):
    PURCHASE_ORDER = (0, __("Purchase Order"))
    SALES_ORDER = (1, __("Sales Order"))
    INVOICE = (2, __("Invoice"))
    CUSTOMER_INQUIRY = (3, __("Customer inquiry"))


ORDER_STATUS.CONFIRMED = [ORDER_STATUS.SALES_ORDER, ORDER_STATUS.INVOICE]


def get_latest_invoice_no(organization):
    """Returns the last invoice number used, 0 if no order has ben invoiced yet."""
    last_invoice_no = db.session.query(sql.functions.max(Order.invoice_no))\
        .filter(Order.organization == organization).first()
    return last_invoice_no[0] if last_invoice_no[0] else 0


def order_amounts_ntuple(base_amount, final_amount, confirmed_amount):
    order_amounts = namedtuple('OrderAmounts', ['base_amount', 'final_amount', 'confirmed_amount'])
    return order_amounts(base_amount, final_amount, confirmed_amount)


class Order(BaseMixin, db.Model):
    __tablename__ = 'customer_order'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('organization_id', 'invoice_no'),
        db.UniqueConstraint('access_token'))

    user_id = db.Column(None, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship(User, backref=db.backref('orders', cascade='all, delete-orphan'))
    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    item_collection = db.relationship('ItemCollection', backref=db.backref('orders', cascade='all, delete-orphan', lazy='dynamic'))

    organization_id = db.Column(None, db.ForeignKey('organization.id'), nullable=False)
    organization = db.relationship('Organization', backref=db.backref('orders', cascade='all, delete-orphan', lazy='dynamic'))

    status = db.Column(db.Integer, default=ORDER_STATUS.PURCHASE_ORDER, nullable=False)

    initiated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    inquired_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    invoiced_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)

    access_token = db.Column(db.Unicode(22), nullable=False, default=buid)

    buyer_email = db.Column(db.Unicode(254), nullable=False)
    buyer_fullname = db.Column(db.Unicode(80), nullable=False)
    buyer_phone = db.Column(db.Unicode(16), nullable=False)
    buyer_company = db.Column(db.Unicode(80), nullable=True)

    invoice_no = db.Column(db.Integer, nullable=True)

    def permissions(self, user, inherited=None):
        perms = super(Order, self).permissions(user, inherited)
        if self.organization.userid in user.organizations_owned_ids():
            perms.add('org_admin')
        return perms

    def register_inquiry(self):
        self.inquired_at = datetime.utcnow()
        self.status = ORDER_STATUS.CUSTOMER_INQUIRY

    def get_amounts(self):
        """
        Calculates and returns the order's base_amount,
        final_amount, confirmed_amount as a namedtuple.

        Note: base_amount, final_amount are calculated for ALL of the order's line items,
        whereas confirmed_amount is calculated only for the order's confirmed line items.
        """
        base_amount = Decimal(0)
        final_amount = Decimal(0)
        confirmed_amount = Decimal(0)
        for line_item in self.line_items:
            base_amount += line_item.base_amount
            final_amount += line_item.final_amount
            if line_item.is_confirmed:
                confirmed_amount += line_item.final_amount
        return order_amounts_ntuple(base_amount, final_amount, confirmed_amount)

    @property
    def is_confirmed(self):
        return self.status in ORDER_STATUS.CONFIRMED


class OrderSession(BaseMixin, db.Model):
    """Records the referrer and utm headers for an order."""
    __tablename__ = 'order_session'
    __uuid_primary_key__ = True

    customer_order_id = db.Column(None, db.ForeignKey('customer_order.id'), nullable=False, index=True, unique=False)
    order = db.relationship(Order, backref=db.backref('session', cascade='all, delete-orphan', uselist=False))

    referrer = db.Column(db.Unicode(2083), nullable=True)

    # Google Analytics parameters
    utm_source = db.Column(db.Unicode(250), nullable=False, default=u"", index=True)
    utm_medium = db.Column(db.Unicode(250), nullable=False, default=u"", index=True)
    utm_term = db.Column(db.Unicode(250), nullable=False, default=u"")
    utm_content = db.Column(db.Unicode(250), nullable=False, default=u"")
    utm_id = db.Column(db.Unicode(250), nullable=False, default=u"", index=True)
    utm_campaign = db.Column(db.Unicode(250), nullable=False, default=u"", index=True)
    # Google click id (for AdWords)
    gclid = db.Column(db.Unicode(250), nullable=False, default=u"", index=True)
