from flask import Flask
from flask.ext.login import current_user
from flask.ext.security import Security, SQLAlchemyUserDatastore
from flask_mail import Mail
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.contrib.fixers import ProxyFix
from flask.ext.admin import Admin, AdminIndexView
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.principal import Principal, identity_loaded
from flask.ext.assets import Environment
from .utils import wtf
from .utils.assets import bundles
from .utils.errors import add_errorhandlers
from .database import db
from .frontend import frontend_blueprint, on_identity_loaded

mail = Mail()


def create_app(configclass):
    application = Flask(__name__, instance_relative_config=True)
    initialise_app(application, configclass)
    return application

def initialise_app(app, configclass):
    # Load the default configuration
    app.config.from_object(configclass)

    # Load the configuration from the instance folder
    try:
        app.config.from_pyfile('config.py')
    except:
        print 'No instance config file'

    if app.config['USE_PROXY']:
        app.wsgi_app = ProxyFix(app.wsgi_app)

    toolbar = DebugToolbarExtension(app)

    db.init_app(app)
    mail.init_app(app)

    assets = Environment(app)
    assets.register(bundles)

    from .models import User, Feed, Entry, Author, Role

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    app.security = Security(app, user_datastore)

    wtf.add_helpers(app)

    admin = Admin(app, 'Admin', index_view=SecuredAdminIndexView())
    admin.add_view(SecuredModelView(User, db.session))
    admin.add_view(SecuredModelView(Feed, db.session))
    admin.add_view(SecuredModelView(Entry, db.session))
    admin.add_view(SecuredModelView(Author, db.session))

    app.register_blueprint(frontend_blueprint)
    identity_loaded.connect_via(app)(on_identity_loaded)

    add_errorhandlers(app)

    Principal(app)

    if not app.debug:
        import logging
        from .utils.loggers import add_logger_filehandler, add_logger_external

        add_logger_filehandler(app)

        if app.config['LOG_ADDRESS']:
            add_logger_external(app)

        app.logger.setLevel(logging.INFO)
        app.logger.info(u'{0} startup'.format(app.config['PROJECT_NAME']))

    return app


# Admin interface
class SecuredAdminIndexView(AdminIndexView):

    def is_accessible(self):
        return current_user.has_role('admin')


class SecuredModelView(ModelView):

    def is_accessible(self):
        return current_user.has_role('admin')
