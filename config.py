DEBUG = True

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECURITY_PASSWORD_HASH = 'bcrypt'
SECURITY_PASSWORD_SALT = 'verysalty'

SQLALCHEMY_DATABASE_URI = 'sqlite://'

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'secretcsrfsession'

SECRET_KEY = 'supersecretkey'

FQDN = 'http://localhost:5000/'

ADMIN_EMAIL = 'admin@localhost.com'
ADMIN_PASSWORD = 'password'