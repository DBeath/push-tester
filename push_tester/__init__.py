from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.contrib.fixers import ProxyFix
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView

app = Flask(__name__)
app.config.from_object('config.BaseConfig')

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