from push_tester import create_app
from push_tester.database import db

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.security import SQLAlchemyUserDatastore
from datetime import datetime

from push_tester.models import User, Role

app = create_app('config.Config')

manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)


@manager.command
def add_admin(email, password):
    """Add an admin user to the database"""

    user = User.query.filter_by(email=email).first()
    if user is not None:
        print 'A user with email {0} already exists'.format(email)
        return

    user = user_datastore.create_user(email=email,
                                      password=password)

    admin_role = user_datastore.find_or_create_role("admin")
    user_datastore.add_role_to_user(user, admin_role)
    user.confirmed_at = datetime.utcnow()
    user_datastore.commit()

    user = User.query.filter_by(email=email).first()
    if user is not None:
        print 'Created admin user: {0}'.format(user.email)
    else:
        print 'Create admin user {0} failed'.format(email)


@manager.command
def delete_user(email):
    """Delete a user from the database"""

    user = User.query.filter_by(email=email).first()
    if user is not None:
        db.session.delete(user)
        db.session.commit()

    user = User.query.filter_by(email=email).first()
    if user is None:
        print 'Deleted user {0}'.format(email)
    else:
        print 'Delete user {0} failed'.format(email)

if __name__ == '__main__':
    manager.run()
