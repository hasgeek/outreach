#: Database backend
SECRET_KEY = 'testkey'
SQLALCHEMY_DATABASE_URI = 'postgres://127.0.0.1/outreach_testing'
SERVER_NAME = 'outreach.travis.dev:6500'
BASE_URL = 'http://' + SERVER_NAME

ALLOWED_ORIGINS = [BASE_URL]
LASTUSER_SERVER = 'https://auth.hasgeek.com'
LASTUSER_CLIENT_ID = ''
LASTUSER_CLIENT_SECRET = ''
TIMEZONE = 'Asia/Calcutta'
