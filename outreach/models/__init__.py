# -*- coding: utf-8 -*-

from flask.ext.sqlalchemy import SQLAlchemy
from outreach import app
from coaster.sqlalchemy import IdMixin, TimestampMixin, BaseMixin, BaseNameMixin

db = SQLAlchemy(app)

from outreach.models.user import *
