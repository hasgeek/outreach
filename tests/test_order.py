import unittest
import json
from outreach import app, init_for
from outreach.models import *
from fixtures import init_data


class TestOrder(unittest.TestCase):

    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        init_for('test')
        db.create_all()
        init_data()
        self.client = app.test_client()

    def test_inquiry(self):
        item = SaleItem.query.filter_by(name='conference-ticket').first()
        data = {
            'line_items': [{'item_id': unicode(item.id), 'quantity': 2}],
            'buyer': {
                'fullname': 'Testing',
                'phone': '9814141414',
                'email': 'test@hasgeek.com',
                'company': 'Acme'
                }
            }
        ic = ItemCollection.query.first()
        resp = self.client.post('/api/1/collection/{ic}/create_order_inquiry'.format(ic=ic.id), data=json.dumps(data), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])
        data = json.loads(resp.data)
        self.assertEquals(resp.status_code, 201)
        order = Order.query.get(data.get('order_id'))
        self.assertEquals(order.status, ORDER_STATUS.CUSTOMER_INQUIRY)
        self.assertEquals(len(order.line_items), 2)

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
