# -*- coding: utf-8 -*-

from datetime import datetime
from decimal import Decimal
from flask import request, jsonify, make_response
from coaster.views import load_models
from baseframe import _
from .. import app
from utils import xhr_only, cors
from ..models import db, LineItem, SaleItem, ItemCollection, User, Order, OrderSession
from ..forms import LineItemForm, BuyerForm, OrderSessionForm
from ..mailclient import send_confirmation_mail


def jsonify_line_items(line_items):
    """
    Serializes and return line items in the format:
    {item_id: {'quantity': Y, 'final_amount': Z}}
    """
    items_json = dict()
    for line_item in line_items:
        item = SaleItem.query.get(line_item.item_id)
        if not items_json.get(unicode(line_item.item_id)):
            items_json[unicode(line_item.item_id)] = {'is_available': item.is_available(), 'quantity': 0, 'final_amount': Decimal(0)}
        if line_item.base_amount is not None:
            items_json[unicode(line_item.item_id)]['base_amount'] = line_item.base_amount
            items_json[unicode(line_item.item_id)]['final_amount'] += line_item.base_amount
        else:
            items_json[unicode(line_item.item_id)]['final_amount'] = None
        items_json[unicode(line_item.item_id)]['quantity'] += 1
        items_json[unicode(line_item.item_id)]['quantity_available'] = item.get_available_quantity()
    return items_json


@app.route('/api/1/order/calculate', methods=['OPTIONS', 'POST'])
@xhr_only
@cors
def calculate():
    """
    Accepts JSON containing an array of line_items, with the quantity and item_id set for each line_item.

    Returns JSON of line items in the format:
    {item_id: {'quantity': Y, 'final_amount': Z}}
    """
    if not request.json or not request.json.get('line_items'):
        return make_response(jsonify(message='Missing line items'), 400)
    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if not line_item_forms:
        return make_response(jsonify(message='Invalid line items'), 400)

    # Make line item splits and compute amounts
    line_items = LineItem.calculate([{'item_id': li_form.data.get('item_id')}
        for li_form in line_item_forms
            for x in range(li_form.data.get('quantity'))])
    items_json = jsonify_line_items(line_items)
    order_final_amount = sum([values['final_amount'] for values in items_json.values() if values['final_amount'] is not None])
    return jsonify(line_items=items_json, order={'final_amount': order_final_amount})


@app.route('/api/1/collection/<item_collection_id>/create_order_inquiry',
           methods=['OPTIONS', 'POST'])
@load_models(
    (ItemCollection, {'id': 'item_collection_id'}, 'item_collection')
    )
@xhr_only
@cors
def create_order_inquiry(item_collection):
    buyer_form = BuyerForm.from_json(request.json.get('buyer'))
    # See comment in BuyerForm about CSRF
    buyer_form.csrf_enabled = False
    if not buyer_form.validate():
        return make_response(jsonify(message='Invalid buyer details'), 400)

    user = User.query.filter_by(email=buyer_form.email.data).first()

    order = Order(user=user,
        organization=item_collection.organization,
        item_collection=item_collection,
        buyer_email=buyer_form.email.data,
        buyer_fullname=buyer_form.fullname.data,
        buyer_company=buyer_form.company.data,
        buyer_phone=buyer_form.phone.data)

    order.make_inquiry()

    line_item_forms = LineItemForm.process_list(request.json.get('line_items'))
    if line_item_forms:
        line_item_tups = LineItem.calculate([{'item_id': li_form.data.get('item_id')}
            for li_form in line_item_forms
                for x in range(li_form.data.get('quantity'))])
        for idx, line_item_tup in enumerate(line_item_tups, start=1):
            item = SaleItem.query.get(line_item_tup.item_id)
            line_item = LineItem(order=order, sale_item=item,
                seq=idx,
                ordered_at=datetime.utcnow(),
                base_amount=line_item_tup.base_amount,
                final_amount=line_item_tup.base_amount)
            db.session.add(line_item)

    db.session.add(order)
    if request.json.get('order_session'):
        order_session_form = OrderSessionForm.from_json(request.json.get('order_session'))
        order_session_form.csrf_enabled = False
        if order_session_form.validate():
            order_session = OrderSession(order=order)
            order_session_form.populate_obj(order_session)
            db.session.add(order_session)
    db.session.commit()
    send_confirmation_mail.delay(order.id, _("Thank you for your interest!"))
    return make_response(jsonify(order_id=order.id, order_access_token=order.access_token), 201)
