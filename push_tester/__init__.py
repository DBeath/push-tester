from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.security import Security, SQLAlchemyUserDatastore

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)

from models import Role, User

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

import push_tester.views