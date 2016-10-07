#!/usr/bin/env python
from outreach import app, init_for
from outreach.models import *
init_for('dev')
app.run('0.0.0.0', debug=True, port=4000)
