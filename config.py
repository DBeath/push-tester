import os

PROJECT_NAME = 'PuSH-Tester'

DEBUG = True

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_TRACKABLE = True

SECURITY_PASSWORD_HASH = 'bcrypt'

SECURITY_PASSWORD_SALT = "0Cd3c-zGAcgE8mJQqWlO6xXq9nLrax3i"
SECURITY_CONFIRM_SALT = "fMcatrYiEcatqj-iX88SpDufjUf9fmrd"
SECURITY_RESET_SALT = "7aN1aWKlXp9aXT9mOGIi86D4-jhaqHXb"
SECURITY_REMEMBER_SALT = "YAZEI0YzVSzo8y0gGLptoYppvJCGrMQj"

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')

CSRF_ENABLED = True
CSRF_SESSION_KEY = 'bEX878f8LR3eHYByk2Dx2LKSxRmaQb4t'

SECRET_KEY = '0CXgQPimsi72T-_XZPWTOKlBiaFuWPdz'

# The Fully Qualified Domain Name where this application runs.
FQDN = 'http://localhost:5000'

# Set to True if using a reverse proxy like Nginx.
USE_PROXY = False

ADMIN_EMAIL = 'admin@localhost.com'
ADMIN_PASSWORD = 'password'

HUB_NAME = 'http://test.superfeedr.com/'

DEBUG_TB_INTERCEPT_REDIRECTS = False

MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'pushtester@gmail.com'
MAIL_PASSWORD = ''

DEFAULT_MAIL_SENDER = ("Push-Tester", "pushtester@gmail.com")
