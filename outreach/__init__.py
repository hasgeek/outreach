# -*- coding: utf-8 -*-

# The imports in this file are order-sensitive

from __future__ import absolute_import
from flask import Flask
from flask.ext.lastuser import Lastuser
from flask.ext.lastuser.sqlalchemy import UserManager
from baseframe import baseframe, assets, Version
import coaster.app
from ._version import __version__
import outreach

version = Version(__version__)

# First, make an app

app = Flask(__name__, instance_relative_config=True)
lastuser = Lastuser()

# Second, import the models and views

from . import models, views
from .models import db

# Third, setup baseframe and assets

assets['jquery-easing.js'][version] = 'js/jquery-easing.js'
assets['agency.js'][version] = 'js/app.js'
assets['classie.js'][version] = 'js/classie.js'
assets['cbpAnimatedHeader.js'][version] = 'js/cbpAnimatedHeader.js'
assets['jqBootstrapValidation.js'][version] = 'js/jqBootstrapValidation.js'

assets['outreach.js'][version] = {'requires': ['jquery-easing.js', 'agency.js', 'classie.js', 'cbpAnimatedHeader.js', 'jqBootstrapValidation.js']}
assets['outreach.css'][version] = 'css/app.css'


# Configure the app
def init_for(env):
    coaster.app.init_app(app, env)
    db.init_app(app)
    db.app = app
    baseframe.init_app(app, requires=['baseframe-bs3', 'outreach'])
    lastuser.init_app(app)
    lastuser.init_usermanager(UserManager(db, outreach.models.User, outreach.models.Team))
