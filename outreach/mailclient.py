# -*- coding: utf-8 -*-

from flask import render_template
from flask.ext.rq import job
from flask.ext.mail import Message
from html2text import html2text
from premailer import transform as email_transform
from .models import Order, LineItem
from . import mail, app


@job('outreach')
def send_confirmation_mail(order_id, subject="Thank you for your order!"):
    """Sends a order confirmation email to the buyer, and CC's it to the organization's contact email."""
    with app.test_request_context():
        order = Order.query.get(order_id)
        msg = Message(subject=subject, recipients=[order.buyer_email], bcc=[order.organization.contact_email])
        line_items = LineItem.query.filter(LineItem.order == order).order_by("seq asc").all()
        html = email_transform(render_template('order_confirmation_mail.html', order=order, org=order.organization, line_items=line_items, base_url=app.config['BASE_URL']))
        msg.html = html
        msg.body = html2text(html)
        mail.send(msg)
