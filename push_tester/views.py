from push_tester import app, db, user_datastore
from flask import render_template, redirect, url_for, g, request, Response
from flask.ext.login import current_user
from flask.ext.security import login_required
from flask.ext.security.utils import encrypt_password
from models import User, Role, Feed, Entry, Author
from forms import AuthorForm, FeedForm, EntryForm
from datetime import datetime
import PyRSS2Gen as RSS2
from rfeed import Item, Feed as rFeed, Guid

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

@app.route('/authors/<int:id>/delete', methods=['POST'])
def delete_author(id):
    author = Author.query.get(id)
    db.session.delete(author)
    db.session.commit()
    return redirect(url_for('authors'))

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
        feed = Feed()
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
def feed(id):
    feed = Feed.query.get(id)
    return render_template('feed.html',
        title='Feed %s' % id,
        feed=feed)

@app.route('/feeds/<int:id>/rss', methods=['GET'])
def feed_rss(id):
    feed = Feed.query.get(id)
    entries = Entry.query.filter_by(feed_id=id).order_by(Entry.published.desc()).limit(10)

    # items = []
    # for entry in entries:
    #     entry_author = ''
    #     for author in entry.authors:
    #         entry_author += repr(author) + ', '
    #     item = RSS2.RSSItem(
    #         title = entry.title,
    #         link = entry.link,
    #         description = entry.content,
    #         guid = entry.guid, 
    #         pubDate = entry.published,
    #         author = entry_author)
    #     items.append(item)

    # rss = RSS2.RSS2(
    #     title=feed.title,
    #     link=feed.topic,
    #     description=feed.description,
    #     lastBuildDate=datetime.utcnow(),
    #     items=items)

    # return rss.to_xml()
    items = []
    for entry in entries:
        entry_author = ''
        for author in entry.authors:
            entry_author += repr(author) + ', '
        item = Item(
            title = entry.title,
            link = entry.link,
            description = entry.content,
            author = entry_author,
            guid = Guid(entry.guid),
            pubDate = entry.published)
        items.append(item)

    rss = rFeed(
        title = feed.title,
        link = feed.topic,
        description = feed.description,
        lastBuildDate = datetime.utcnow(),
        language = "en-US",
        items = items)

    f = open('rss.xml', 'w')
    f.write(rss.rss())
    f.close()

    return rss.rss()

@app.route('/feeds/<int:id>/delete', methods=['POST'])
def delete_feed(id):
    feed = Feed.query.get(id)
    for entry in feed.entries:
        db.session.delete(entry)
    db.session.delete(feed)
    db.session.commit()
    return redirect(url_for('feeds'))

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
def delete_entry(id):
    entry = Entry.query.get(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for('entries'))