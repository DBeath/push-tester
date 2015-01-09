from push_tester import app, db, user_datastore
from flask import render_template, redirect, url_for, g, request, Response, make_response, abort
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.ext.security.utils import encrypt_password
from flask.ext.principal import identity_loaded, Permission, RoleNeed, UserNeed
from models import User, Role, Feed, Entry, Author
from forms import AuthorForm, FeedForm, EntryForm
from datetime import datetime
import PyRSS2Gen as RSS2
from rfeed import Item, Feed as rFeed, Guid, Serializable
from link_header import Link, LinkHeader
from collections import namedtuple
from functools import partial
import requests

FeedNeed = namedtuple('feed', ['method', 'value'])
ViewFeedNeed = partial(FeedNeed, 'view')

class ViewFeedPermission(Permission):
    def __init__(self, feed_id):
        need = ViewFeedNeed(unicode(feed_id))
        super(ViewFeedPermission, self).__init__(need)

EntryNeed = namedtuple('entry', ['method', 'value'])
ViewEntryNeed = partial(EntryNeed, 'view')

class ViewEntryPermission(Permission):
    def __init__(self, entry_id):
        need = ViewEntryNeed(unicode(entry_id))
        super(ViewEntryPermission, self).__init__(need)

AuthorNeed = namedtuple('author', ['method', 'value'])
ViewAuthorNeed = partial(AuthorNeed, 'view')

class ViewAuthorPermission(Permission):
    def __init__(self, author_id):
        need = ViewAuthorNeed(unicode(author_id))
        super(ViewAuthorPermission, self).__init__(need)

@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user

    if hasattr(current_user, 'feeds'):
        for feed in current_user.feeds:
            identity.provides.add(ViewFeedNeed(unicode(feed.id)))

    if hasattr(current_user, 'entries'):
        for entry in current_user.entries:
            identity.provides.add(ViewEntryNeed(unicode(entry.id)))

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
    entry_count = Entry.query.count()
    author_count = Author.query.count()
    feed_count = Feed.query.count()
    return render_template('index.html',
        author_count=author_count,
        entry_count=entry_count,
        feed_count=feed_count,
        title='Home')


@app.route('/create_entry')
@login_required
def create_entry():
    return redirect(url_for('index'))

@app.route('/authors')
@login_required
def authors():
    authors = Author.query.filter_by(user_id=current_user.id)
    return render_template('authors.html',
        authors=authors,
        title='Authors')

@app.route('/authors/new', methods=['GET', 'POST'])
@login_required
def new_author():
    form = AuthorForm()
    if request.method == 'POST' and form.validate():
        author = Author(name=form.name.data, email=form.email.data)
        author.user = current_user
        db.session.add(author)
        db.session.commit()
        return redirect(url_for('authors'))
    return render_template('new_author.html',
        title='New Author',
        form=form)

@app.route('/authors/<int:id>/delete', methods=['POST'])
@login_required
def delete_author(id):
    permission = ViewAuthorPermission(id)

    if permission.can():
        author = Author.query.get(id)
        db.session.delete(author)
        db.session.commit()
        return redirect(url_for('authors'))

    abort(403)


@app.route('/feeds')
@login_required
def feeds():
    feeds = Feed.query.filter_by(user_id=current_user.id)
    return render_template('feeds.html',
        feeds=feeds,
        title='Feeds')

@login_required
@app.route('/feeds/new', methods=['GET', 'POST'])
def new_feed():
    form = FeedForm()
    if request.method == 'POST' and form.validate():
        feed = Feed()
        feed.user = current_user
        feed.title = form.title.data
        feed.description = form.description.data
        feed.hub = form.hub.data
        db.session.add(feed)
        db.session.flush()
        feed.topic = app.config['FQDN'] + '/feeds/%s' % feed.id
        db.session.commit()
        return redirect(url_for('feeds'))
    return render_template('new_feed.html',
        title='New Feed',
        form=form)

@app.route('/feeds/<int:id>', methods=['GET'])
@login_required
def feed(id):
    permission = ViewFeedPermission(id)

    if permission.can():
        feed = Feed.query.get(id)
        return render_template('feed.html',
            title='Feed %s' % id,
            feed=feed,
            entries = feed.entries)

    abort(403)

@app.route('/feeds/<int:id>/rss', methods=['GET'])
@login_required
def feed_rss(id):
    permission = ViewFeedPermission(id)

    if permission.can():
        feed = Feed.query.get(id)

        rss = feed.rss()

        f = open('rss.xml', 'w')
        f.write(rss.rss())
        f.close()

        headers = {}
        headers['Link'] = str(LinkHeader([
            Link(feed.hub, rel="hub"),
            Link(feed.topic, rel="self")]))

        return make_response(rss.rss(), 200, headers)

    abort(403)

@app.route('/feeds/<int:id>/ping', methods=['POST'])
@login_required
def feed_ping(id):
    permission = ViewFeedPermission(id)

    if permission.can():
        feed = Feed.query.get(id)
        ping_hub(feed.hub, feed.topic)

    abort(403)

@app.route('/feeds/<int:id>/delete', methods=['POST'])
@login_required
def delete_feed(id):
    permission = ViewFeedPermission(id)

    if permission.can():
        feed = Feed.query.get(id)
        for entry in feed.entries:
            db.session.delete(entry)
        db.session.delete(feed)
        db.session.commit()
        return redirect(url_for('feeds'))

    abort(403)

@app.route('/entries')
@login_required
def entries():
    entries = Entry.query.filter_by(user_id=current_user.id)
    return render_template('entries.html',
        title='Entries',
        entries=entries)

@app.route('/entries/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    form = EntryForm()
    form.feed.choices = [(f.id, f.topic) for f in Feed.query.filter_by(user_id=current_user.id)]
    form.authors.choices = [(a.id, a.name) for a in Author.query.filter_by(user_id=current_user.id)]
    if request.method == 'POST' and form.validate():
        entry = Entry()
        entry.user = current_user
        entry.title = form.title.data
        entry.published = form.published.data if form.published.data else datetime.utcnow()
        entry.updated = form.updated.data
        entry.content = form.content.data
        entry.summary = form.summary.data
        entry.feed_id = form.feed.data
        for a in form.authors.data:
            author = Author.query.get(a)
            entry.authors.append(author)
        db.session.add(entry)

        db.session.flush()
        entry.guid = app.config['FQDN'] + '/entries/%s' % entry.id
        entry.link = entry.guid
        db.session.commit()
        return redirect(url_for('entries'))

    return render_template('new_entry.html',
        title='New Entry',
        form=form)

@app.route('/entries/<int:id>/delete', methods=['POST'])
@login_required
def delete_entry(id):
    permission = ViewEntryPermission(id)

    if permission.can():
        entry = Entry.query.get(id)
        db.session.delete(entry)
        db.session.commit()
        return redirect(url_for('entries'))

    abort(403)

def ping_hub(hub, topic):
    params = {
        'hub.mode': 'publish',
        'hub.url': topic
    }
    return requests.post(hub, params)