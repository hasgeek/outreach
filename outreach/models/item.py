# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.orderinglist import ordering_list
from ..models import db, BaseScopedNameMixin, MarkdownColumn
from ..models import ItemCollection


__all__ = ['Item', 'ItemImage', 'Price']

item_category = db.Table('item_category', db.Model.metadata,
    db.Column('item_id', None, db.ForeignKey('item.id'), primary_key=True),
    db.Column('category_id', None, db.ForeignKey('category.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow, nullable=False))


class Item(BaseScopedNameMixin, db.Model):
    """Represents an item in the item collection."""

    __tablename__ = 'item'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('item_collection_id', 'name'),)

    description = MarkdownColumn('description', default=u'', nullable=False)
    seq = db.Column(db.Integer, nullable=False)

    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    item_collection = db.relationship(ItemCollection,
        backref=db.backref('items', cascade='all, delete-orphan', order_by=seq,
            collection_class=ordering_list('seq', count_from=1)))

    parent = db.synonym('item_collection')

    categories = db.relationship('Category', secondary=item_category)

    quantity_total = db.Column(db.Integer, default=0, nullable=False)

    cancellable_until = db.Column(db.DateTime, nullable=True)

    def current_price(self):
        """Return the current price object for an item."""
        return self.price_at(datetime.utcnow())

    def price_at(self, timestamp):
        """Return the price object for an item at a given time."""
        return Price.query.filter(Price.item == self, Price.start_at <= timestamp,
            Price.end_at > timestamp).order_by('created_at desc').first()  # noqa

    @classmethod
    def get_by_category(cls, category):
        return cls.query.filter(Item.category == category).order_by('seq')

    @hybrid_property
    def quantity_available(self):
        return self.quantity_total - self.get_confirmed_line_items.count()

    @property
    def is_available(self):
        """Checks if an item has a current price object and has a positive quantity_available"""
        return bool(self.current_price() and self.quantity_available > 0)


class ItemImage(BaseScopedNameMixin, db.Model):
    """
    Represents a single image in an item's image collection.
    The image collection can contain exactly one primary image
    """

    __tablename__ = 'item_image'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('item_id', 'name'),
        db.UniqueConstraint('item_id', 'primary'))

    url = db.Column(db.Unicode(2083), nullable=False)
    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False, index=True)
    item = db.relationship(Item, backref=db.backref('images', cascade='all, delete-orphan'))
    parent = db.synonym('item')
    primary = db.Column(db.Boolean, nullable=True, default=None)

    def set_as_primary(self):
        self.primary = True


class Price(BaseScopedNameMixin, db.Model):
    __tablename__ = 'price'
    __uuid_primary_key__ = True
    __table_args__ = (db.UniqueConstraint('item_id', 'name'),
        db.CheckConstraint('start_at < end_at', 'price_start_at_lt_end_at_check'))

    item_id = db.Column(None, db.ForeignKey('item.id'), nullable=False)
    item = db.relationship(Item, backref=db.backref('prices', cascade='all, delete-orphan'))

    parent = db.synonym('item')
    start_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_at = db.Column(db.DateTime, nullable=False)

    amount = db.Column(db.Numeric, default=Decimal(0), nullable=False)
    currency = db.Column(db.Unicode(3), nullable=False, default=u'INR')
