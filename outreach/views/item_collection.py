# -*- coding: utf-8 -*-

from flask import make_response, render_template, jsonify, request
from coaster.views import load_models
from .. import app
from ..models import ItemCollection, SaleItem
from utils import xhr_only, cors


def jsonify_item(item):
    price = item.current_price()
    if price:
        return {
            'name': item.name,
            'title': item.title,
            'id': item.id,
            'image': {'url': item.images[0].url, 'title': item.images[0].title} if item.images else None,
            'description': item.description.text,
            'quantity_available': item.quantity_available,
            'is_available': item.is_available,
            'category_id': item.category_id,
            'item_collection_id': item.item_collection_id,
            'price': price.amount,
            'price_category': price.title,
            'price_valid_upto': price.end_at
        }


def jsonify_category(category):
    category_items = []
    for item in SaleItem.get_by_category(category):
        item_json = jsonify_item(item)
        if item_json:
            category_items.append(item_json)
    if category_items:
        return {
            'id': category.id,
            'title': category.title,
            'description': category.description.text,
            'name': category.name,
            'item_collection_id': category.item_collection_id,
            'items': category_items
        }


@app.route('/api/1/outreach.js')
@cors
def outreachjs():
    return make_response(jsonify({
        'script': render_template('outreach.js', base_url=request.url_root.strip('/'),
        razorpay_key_id=app.config['RAZORPAY_KEY_ID'])
    }))


@app.route('/ic/<item_collection>', methods=['GET', 'OPTIONS'])
@load_models(
    (ItemCollection, {'id': 'item_collection'}, 'item_collection')
    )
@xhr_only
@cors
def item_collection(item_collection):
    categories_json = []
    for category in item_collection.categories:
        category_json = jsonify_category(category)
        if category_json:
            categories_json.append(category_json)
    return jsonify(html=render_template('outreach.html'), categories=categories_json, refund_policy=item_collection.details.get('refund_policy', ''))
