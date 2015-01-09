DEBUG = True

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'verysalty'
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secretcsrfsession'

SECRET_KEY = 'supersecretkey'

FQDN = 'http://localhost:5000'

ADMIN_EMAIL = 'admin@localhost.com'
ADMIN_PASSWORD = 'password'

HUB_NAME = 'http://test.superfeedr.com/'

DEBUG_TB_INTERCEPT_REDIRECTS = False