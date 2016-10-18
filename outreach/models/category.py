# -*- coding: utf-8 -*-

from ..models import db, BaseScopedNameMixin, ItemCollection, MarkdownColumn
from sqlalchemy.ext.orderinglist import ordering_list

__all__ = ['Category']


class Category(BaseScopedNameMixin, db.Model):
    """Represents a category of items."""

    __tablename__ = 'category'
    __table_args__ = (db.UniqueConstraint('item_collection_id', 'name'), db.UniqueConstraint('item_collection_id', 'seq'))

    item_collection_id = db.Column(None, db.ForeignKey('item_collection.id'), nullable=False)
    seq = db.Column(db.Integer, nullable=False)
    description = MarkdownColumn('description', default=u"", nullable=False)
    item_collection = db.relationship(ItemCollection, backref=db.backref('categories',
                        cascade='all, delete-orphan', order_by=seq, collection_class=ordering_list('seq', count_from=1)))

    parent = db.synonym('item_collection')
