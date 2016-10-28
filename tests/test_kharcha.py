import json
import unittest
from flask import url_for
from outreach import app, init_for
from outreach.models import (db, SaleItem)
from fixtures import init_data


class TestKharchaAPI(unittest.TestCase):

    def setUp(self):
        self.ctx = app.test_request_context()
        self.ctx.push()
        init_for('test')
        db.drop_all()
        db.create_all()
        init_data()
        self.client = app.test_client()

    def test_basic_kharcha_workflow(self):
        first_item = SaleItem.query.filter_by(name='conference-ticket').first()
        quantity = 2
        kharcha_req = {'line_items': [{'item_id': unicode(first_item.id), 'quantity': quantity}]}
        resp = self.client.post(url_for('calculate'), data=json.dumps(kharcha_req), content_type='application/json', headers=[('X-Requested-With', 'XMLHttpRequest'), ('Origin', app.config['BASE_URL'])])

        self.assertEquals(resp.status_code, 200)
        resp_json = json.loads(resp.get_data())
        # Test that the price is correct
        self.assertEquals(resp_json.get('line_items')[unicode(first_item.id)].get('final_amount'),
            quantity * first_item.current_price().amount)

    def tearDown(self):
        db.session.rollback()
        db.drop_all()
        self.ctx.pop()
