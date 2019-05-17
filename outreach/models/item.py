# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.orderinglist import ordering_list
from . import db, BaseScopedNameMixin, MarkdownColumn, ItemCollection, Category


__all__ = ['InventoryItem', 'SaleItem', 'SaleItemImage', 'Price']

inventory_item_sale_item = db.Table('inventory_item_sale_item', db.Model.metadata,
    db.Column('sale_item_id', None, db.ForeignKey('sale_item.id'), primary_key=True),
    db.Column('inventory_item_id', None, db.ForeignKey('inventory_item.id'), primary_key=True, index=True),
    db.Column('created_at', db.DateTime, default=db.func.utcnow(), nullable=False))


class InventoryItem(BaseScopedNameMixin, db.Model):
    """Represents an inventory item."""

    __tablename__ = 'inventory_item'
    __uuid_primary_key__ = True

    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    item_collection = db.relationship(ItemCollection, backref=db.backref('inventory_items', cascade='all, delete-orphan'))
    parent = db.synonym('item_collection')
    quantity_total = db.Column(db.Integer, default=0, nullable=False)
    cancellable_until = db.Column(db.DateTime, nullable=True)
    sale_items = db.relationship('SaleItem', secondary=inventory_item_sale_item, backref=db.backref('inventory_items'))


class SaleItem(BaseScopedNameMixin, db.Model):
    """Represents a sale item."""

    __tablename__ = 'sale_item'
    __uuid_primary_key__ = True

    seq = db.Column(db.Integer, nullable=False)
    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    item_collection = db.relationship(ItemCollection, backref=db.backref('sale_items', cascade='all, delete-orphan', lazy='dynamic'))
    parent = db.synonym('item_collection')
    category_id = db.Column(None, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship(Category, backref=db.backref('sale_items', cascade='all, delete-orphan',
        order_by=seq,
        collection_class=ordering_list('seq', count_from=1)))
    #: Call to action text
    blurb = MarkdownColumn('blurb', default=u"", nullable=False)
    description = MarkdownColumn('description', default=u"", nullable=False)

    def current_price(self):
        """Return the current price object for an item."""
        return self.price_at(datetime.utcnow())

    def price_at(self, timestamp):
        """Return the price object for an item at a given time."""
        return Price.query.filter(Price.sale_item == self, Price.start_at <= timestamp,
            Price.end_at > timestamp).order_by(Price.created_at.desc()).first()

    def is_available(self):
        """Checks if an item has a current price object and has a positive quantity_available"""
        if not self.current_price():
            return False
        for inventory_item in self.inventory_items:
            if self.confirmed_line_items.count() >= inventory_item.quantity_total:
                return False
        return True

    def get_available_quantity(self):
        """
        Checks the associated inventory items, computes the quantity available in each inventory item
        and returns the maximum quantity available. Returns 0 if the computed quantity_available is <= 0.
        """
        available_quantity = min([inventory_item.quantity_total - self.confirmed_line_items.count()
            for inventory_item in self.inventory_items])
        return max(available_quantity, 0)


class SaleItemImage(BaseScopedNameMixin, db.Model):
    """
    Represents a single image in an item's image collection.
    The image collection can contain exactly one primary image
    """

    __tablename__ = 'sale_item_image'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('sale_item_id', 'name'), )

    url = db.Column(db.Unicode(2083), nullable=False)
    seq = db.Column(db.Integer, nullable=False)
    sale_item_id = db.Column(None, db.ForeignKey('sale_item.id'), nullable=False, index=True)
    sale_item = db.relationship(SaleItem, backref=db.backref('images', cascade='all, delete-orphan',
        order_by=seq,
        collection_class=ordering_list('seq', count_from=1)))
    parent = db.synonym('sale_item')


class Price(BaseScopedNameMixin, db.Model):
    __tablename__ = 'price'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('sale_item_id', 'name'),
        db.CheckConstraint('start_at < end_at', 'price_start_at_lt_end_at_check'))

    sale_item_id = db.Column(None, db.ForeignKey('sale_item.id'), nullable=False)
    sale_item = db.relationship(SaleItem, backref=db.backref('prices', cascade='all, delete-orphan'))
    parent = db.synonym('sale_item')
    start_at = db.Column(db.DateTime, default=db.func.utcnow(), nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')
