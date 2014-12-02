from push_tester import app, db, user_datastore
from flask import render_template, redirect, url_for, g, request, Response
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.ext.security.utils import encrypt_password
from models import User, Role, Feed, Entry, Author
from forms import AuthorForm, FeedForm, EntryForm

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

@app.route('/authors')
def authors():
    authors = Author.query.all()
    return render_template('authors.html',
        authors=authors,
        title='Authors')

@app.route('/authors/new', methods=['GET', 'POST'])
def new_author():
    form = AuthorForm()
    if request.method == 'POST' and form.validate():
        author = Author(name=form.name.data, email=form.email.data)
        db.session.add(author)
        db.session.commit()
        return redirect(url_for('authors'))
    return render_template('new_author.html',
        title='New Author',
        form=form)

@app.route('/feeds')
def feeds():
    feeds = Feed.query.all()
    return render_template('feeds.html',
        feeds=feeds,
        title='Feeds')

@app.route('/feeds/new', methods=['GET', 'POST'])
def new_feed():
    form = FeedForm()
    if request.method == 'POST' and form.validate():
        feed = Feed(topic=form.topic.data)
        feed.description = form.description.data
        feed.hub = form.hub.data
        db.session.add(feed)
        db.session.commit()
        return redirect(url_for('feeds'))
    return render_template('new_feed.html',
        title='New Feed',
        form=form)

@app.route('/entries')
def entries():
    entries = Entry.query.all()
    return render_template('entries.html',
        title='Entries',
        entries=entries)

@app.route('/entries/new', methods=['GET', 'POST'])
def new_entry():
    authors = Author.query.all()
    form = EntryForm()
    feeds = Feed.query.all()
    print feeds
    form.feed.choices = [(f.id, f.topic) for f in Feed.query.all()]
    form.authors.choices = [(a.id, a.name) for a in Author.query.all()]
    if request.method == 'POST' and form.validate():
        entry = Entry()
        db.session.add(entry)
        db.commit()
        return redirect(url_for('entries'))
    return render_template('new_entry.html',
        title='New Entry',
        form=form)