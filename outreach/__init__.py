# -*- coding: utf-8 -*-

from pytz import timezone
from flask import Flask
from flask_rq import RQ
from flask_mail import Mail
from flask_lastuser import Lastuser
from flask_lastuser.sqlalchemy import UserManager
from flask_admin import Admin
import wtforms_json
from baseframe import baseframe, assets, Version
from ._version import __version__
import coaster.app


app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

mail = Mail()

# --- Assets ------------------------------------------------------------------

version = Version(__version__)
assets['outreach.css'][version] = 'css/app.css'
assets['outreach.js'][version] = 'js/scripts.js'


from . import extapi, views  # NOQA
from outreach.models import db, Order, User, InventoryItem, SaleItem, SaleItemImage, Price, ItemCollection, Organization, Category  # noqa


def init_flask_admin():
    from siteadmin import ItemCollectionModelView, InventoryItemModelView, SaleItemModelView, SaleItemImageView, PriceModelView, OrganizationModelView, CategoryModelView, OrderModelView  # noqa
    try:
        admin = Admin(app, name="Outreach Admin", template_mode='bootstrap3', url='/siteadmin')
        admin.add_view(OrganizationModelView(Organization, db.session))
        admin.add_view(ItemCollectionModelView(ItemCollection, db.session))
        admin.add_view(CategoryModelView(Category, db.session))
        admin.add_view(InventoryItemModelView(InventoryItem, db.session))
        admin.add_view(SaleItemModelView(SaleItem, db.session))
        admin.add_view(SaleItemImageView(SaleItemImage, db.session))
        admin.add_view(PriceModelView(Price, db.session))
        admin.add_view(OrderModelView(Order, db.session))
    except AssertionError:
        # AssertionError is ignored because of blueprint collisions that occur while running tests
        # See https://github.com/flask-admin/flask-admin/issues/910
        pass


# Configure the app
def init_for(env):
    coaster.app.init_app(app, env)
    db.init_app(app)
    db.app = app

    RQ(app)

    lastuser.init_app(app)
    lastuser.init_usermanager(UserManager(db, User))
    app.config['tz'] = timezone(app.config['TIMEZONE'])
    baseframe.init_app(app, requires=['outreach'], ext_requires=['baseframe-bs3', 'fontawesome>=4.0.0', 'ractive', 'ractive-transitions-fly', 'validate', 'nprogress', 'baseframe-footable'])

    mail.init_app(app)
    wtforms_json.init()

    init_flask_admin()
