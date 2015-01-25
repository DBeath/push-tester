from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.security.utils import encrypt_password
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.contrib.fixers import ProxyFix
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from datetime import datetime

app = Flask(__name__, instance_relative_config=True)

# Load the default configuration
app.config.from_object('config')

# Load the configuration from the instance folder
app.config.from_pyfile('config.py')

if app.config['USE_PROXY']:
	app.wsgi_app = ProxyFix(app.wsgi_app)

toolbar = DebugToolbarExtension(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mail = Mail(app)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

from models import Role, User

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from .utils import wtf, assets
wtf.add_helpers(app)


from .views import *
from .errors import *
from .models import User, Feed, Entry, Author

# Admin interface
class SecuredAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.has_role('admin')


class SecuredModelView(ModelView):
    def is_accessible(self):
        return current_user.has_role('admin')


admin = Admin(app, 'Admin', index_view=SecuredAdminIndexView())
admin.add_view(SecuredModelView(User, db.session))
admin.add_view(SecuredModelView(Feed, db.session))
admin.add_view(SecuredModelView(Entry, db.session))
admin.add_view(SecuredModelView(Author, db.session))

@manager.command
def add_admin(email, password):
    """Add an admin user to your database"""
    user = user_datastore.create_user(email=email,
        password=encrypt_password(password))

    admin_role = user_datastore.find_or_create_role("admin")
    user_datastore.add_role_to_user(user, admin_role)
    user.confirmed_at = datetime.utcnow()

    db.session.commit()
    print "Created admin user: %s" % (user, )