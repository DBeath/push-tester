from flask import current_app as app
from . import frontend_blueprint as frontend
from ..database import db
from flask import render_template, redirect, url_for, request, make_response, \
    abort, flash
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.ext.principal import identity_loaded, Permission, RoleNeed
from datetime import datetime
from link_header import Link, LinkHeader
from collections import namedtuple
from functools import partial
from ..models import Feed, Entry, Author
from ..forms import AuthorForm, FeedForm, EntryForm
from ..utils.bootstrap import ALERT


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

admin_permission = Permission(RoleNeed('admin'))


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user

    if hasattr(current_user, 'feeds'):
        for feed in current_user.feeds:
            identity.provides.add(ViewFeedNeed(unicode(feed.id)))

    if hasattr(current_user, 'entries'):
        for entry in current_user.entries:
            identity.provides.add(ViewEntryNeed(unicode(entry.id)))


@frontend.route('/')
def index():
    if current_user.is_authenticated():
        entry_count = Entry.query.filter_by(user_id=current_user.id).count()
        author_count = Author.query.filter_by(user_id=current_user.id).count()
        feed_count = Feed.query.filter_by(user_id=current_user.id).count()

        return render_template('home.html',
            author_count=author_count,
            entry_count=entry_count,
            feed_count=feed_count,
            title='Home')

    return render_template('index.html',
        title='Home')


@frontend.route('/create_entry')
@login_required
def create_entry():
    return redirect(url_for('frontend.index'))


@frontend.route('/authors')
@login_required
def authors():
    authors = Author.query.filter_by(user_id=current_user.id)
    return render_template('authors.html',
        authors=authors,
        title='Authors')


@frontend.route('/authors/new', methods=['GET', 'POST'])
@login_required
def new_author():
    form = AuthorForm()
    if request.method == 'POST' and form.validate():
        author = Author(name=form.name.data, email=form.email.data)
        author.user = current_user
        db.session.add(author)
        db.session.commit()
        return redirect(url_for('frontend.authors'))
    return render_template('new_author.html',
        title='New Author',
        new_author_form=form)


@frontend.route('/authors/<int:id>/delete', methods=['POST'])
@login_required
def delete_author(id):
    permission = ViewAuthorPermission(id)

    if permission.can():
        author = Author.query.get(id)
        db.session.delete(author)
        db.session.commit()
        return redirect(url_for('frontend.authors'))

    abort(403)


@frontend.route('/feeds')
@login_required
def feeds():
    feeds = Feed.query.filter_by(user_id=current_user.id)
    return render_template('feeds.html',
        feeds=feeds,
        title='Feeds')


@login_required
@frontend.route('/feeds/new', methods=['GET', 'POST'])
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
        flash(u'{0} was successfully created'.format(feed.title), ALERT.SUCCESS)
        return redirect(url_for('feeds'))
    return render_template('new_feed.html',
        title='New Feed',
        new_feed_form=form)


@frontend.route('/feeds/<int:id>', methods=['GET'])
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


@frontend.route('/feeds/<int:id>/rss', methods=['GET'])
def feed_rss(id):
    feed = Feed.query.get(id)

    rss = feed.rss()

    f = open('rss.xml', 'w')
    f.write(rss.rss())
    f.close()

    headers = {}
    headers['Link'] = str(LinkHeader([
        Link(feed.hub, rel="hub"),
        Link(feed.get_rss_url(), rel="self")]))

    return make_response(rss.rss(), 200, headers)


@frontend.route('/feeds/<int:id>/ping', methods=['POST'])
@login_required
def feed_ping(id):
    permission = ViewFeedPermission(id)

    if permission.can():
        feed = Feed.query.get(id)
        message = feed.ping_hub()
        flash(message[0], message[1])
        return redirect(url_for('frontend.feeds'))

    abort(403)


@frontend.route('/feeds/<int:id>/delete', methods=['POST'])
@login_required
def delete_feed(id):
    permission = ViewFeedPermission(id)

    if permission.can():
        feed = Feed.query.get(id)
        for entry in feed.entries:
            db.session.delete(entry)
        db.session.delete(feed)
        db.session.commit()
        return redirect(url_for('frontend.feeds'))

    abort(403)


@frontend.route('/entries')
@login_required
def entries():
    entries = Entry.query.filter_by(user_id = current_user.id).order_by(Entry.published.desc())
    return render_template('entries.html',
        title='Entries',
        entries=entries)


@frontend.route('/entries/new', methods=['GET', 'POST'])
@frontend.route('/entries/new/<feed_id>', methods=['GET', 'POST'])
@login_required
def new_entry(*feed_id):
    if feed_id:
        feeds = Feed.query.filter_by(user_id=current_user.id, id=feed_id).all()
    else:
        feeds = Feed.query.filter_by(user_id=current_user.id).all()

    if not feeds:
        flash(u'You must create a Feed first', ALERT.WARNING)
        return redirect(url_for('frontend.new_feed'))

    form = EntryForm()
    form.feed.choices = [(f.id, repr(f)) for f in feeds]
    form.authors.choices = [(a.id, repr(a)) for a in Author.query.filter_by(user_id=current_user.id).all()]
    
    if request.method == 'POST':
        print form.published
        print form.published.data

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

        if form.ping.data:
            feed = Feed.query.get(form.feed.data)
            message = feed.ping_hub()
            flash(message[0], message[1])
        return redirect(url_for('entries'))

    return render_template('new_entry.html',
        title='New Entry',
        new_entry_form=form)


@frontend.route('/entries/<int:id>/delete', methods=['POST'])
@login_required
def delete_entry(id):
    permission = ViewEntryPermission(id)

    if permission.can():
        entry = Entry.query.get(id)
        db.session.delete(entry)
        db.session.commit()
        return redirect(url_for('frontend.entries'))

    abort(403)
