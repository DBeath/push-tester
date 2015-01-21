from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.contrib.fixers import ProxyFix

app = Flask(__name__)
app.config.from_object('config.BaseConfig')

if app.config['USE_PROXY']:
	app.wsgi_app = ProxyFix(app.wsgi_app)

toolbar = DebugToolbarExtension(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)

from models import Role, User

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

from utils import wtf
wtf.add_helpers(app)

import push_tester.views