#!/usr/bin/env python

from outreach.models import *
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def init_data():
    db.drop_all()
    db.create_all()

    user = User(userid="U3_JesHfQ2OUmdihAXaAGQ", email="test@hasgeek.com")
    db.session.add(user)
    db.session.commit()

    one_month_from_now = date.today() + relativedelta(months=+1)

    hasgeek = Organization(title='HasGeek', userid="U3_JesHfQ2OUmdihAXaAGQ",
        status=0, contact_email=u'test@gmail.com',
        details={'service_tax_no': 'xx', 'address': u'<h2 class="company-name">XYZ</h2> <p>Bangalore - 560034</p> <p>India</p>', 'cin': u'1234', 'pan': u'abc', 'website': u'https://www.test.com', 'refund_policy': u'<p>We offer full refund.</p>', 'support_email': 'test@boxoffice.com', 'ticket_faq': '<p>To cancel your ticket, please mail <a href="mailto:test@boxoffice.com">test@boxoffice.com</a> with your receipt number.</p>'})
    db.session.add(hasgeek)
    db.session.commit()

    rc2016 = ItemCollection(title='2016', organization=hasgeek)
    db.session.add(rc2016)
    db.session.commit()

    day1 = InventoryItem(title='day1', organization=hasgeek, quantity_total=1000)
    db.session.add(day1)
    day2 = InventoryItem(title='day2', organization=hasgeek, quantity_total=1000)
    db.session.add(day2)

    category_conference = Category(title='Conference', item_collection=rc2016, seq=1)
    db.session.add(category_conference)
    category_workshop = Category(title='Workshop', item_collection=rc2016, seq=2)
    db.session.add(category_workshop)
    category_merch = Category(title='Merchandise', item_collection=rc2016, seq=3)
    db.session.add(category_merch)
    db.session.commit()

    # import IPython; IPython.embed()
    with db.session.no_autoflush:
        conf_ticket = SaleItem(title='Conference ticket', description='<p><i class="fa fa-calendar"></i>14 - 15 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th and 15th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name='conference').first(), seq=1)
        conf_ticket.inventory_items.append(day1)
        conf_ticket.inventory_items.append(day2)
        rc2016.sale_items.append(conf_ticket)
        db.session.commit()

        price = Price(sale_item=conf_ticket, title='Super Early Geek', start_at=datetime.utcnow(), end_at=one_month_from_now, amount=3500)
        db.session.add(price)
        db.session.commit()

        single_day_conf_ticket = SaleItem(title='Single Day', description='<p><i class="fa fa-calendar"></i>14 April 2016</p><p><i class="fa fa-map-marker ticket-venue"></i>MLR Convention Center, JP Nagar</p><p>This ticket gets you access to rootconf conference on 14th April 2016.</p>', item_collection=rc2016, category=Category.query.filter_by(name='conference').first(), seq=2)
        single_day_conf_ticket.inventory_items.append(day1)
        rc2016.sale_items.append(single_day_conf_ticket)
        db.session.commit()

        single_day_price = Price(sale_item=single_day_conf_ticket, title='Single Day', start_at=datetime.utcnow(), end_at=one_month_from_now, amount=2500)
        db.session.add(single_day_price)
        db.session.commit()
