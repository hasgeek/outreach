#!/usr/bin/env python
from outreach import app
from outreach.models import *
app.run('0.0.0.0', debug=True, port=4000)
