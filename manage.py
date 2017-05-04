#!/usr/bin/env python

from coaster.manage import init_manager

import outreach
import outreach.models as models
import outreach.views as views
from outreach.models import db
from outreach import app


if __name__ == '__main__':
    db.init_app(app)
    manager = init_manager(app, db, outreach=outreach, models=models, views=views)

    manager.run()
