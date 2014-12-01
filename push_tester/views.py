from push_tester import app, db, user_datastore
from flask import render_template, redirect, url_for, g
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.ext.security.utils import encrypt_password
from models import User, Role

@app.before_first_request
def create_admin_user():
    db.create_all()
    adminRole = user_datastore.find_or_create_role(
        name='admin', 
        description='Admin Role')
    db.session.add(adminRole)
    if user_datastore.find_user(email=app.config['ADMIN_EMAIL']) is None:
        adminUser = user_datastore.create_user(
            email=app.config['ADMIN_EMAIL'],
            password=encrypt_password(app.config['ADMIN_PASSWORD']))
        user_datastore.add_role_to_user(adminUser, adminRole)
        user_datastore.activate_user(adminUser)
        db.session.add(adminUser)
    db.session.commit()
    
@app.before_request
def before_request():
    g.user = current_user

@app.route('/')
def index():
    return render_template('index.html',
        title='Home')

@app.route('/create_entry')
def create_entry():
    return redirect(url_for('index'))