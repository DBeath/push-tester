from push_tester import db, app
from flask.ext.security import UserMixin, RoleMixin
from rfeed import Item, Feed as rFeed, Guid, Serializable
from datetime import datetime

class PushLink(Serializable):
    def __init__(self, rel=None, href=None, xmlns=None):
        Serializable.__init__(self)

        self.rel = rel
        self.href = href
        self.xmlns = xmlns

    def publish(self, handler):
        Serializable.publish(self, handler)
        handler.startElement("link", {"rel": self.rel, "href": self.href, "xmlns": self.xmlns})
        handler.endElement("link")


roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    feeds = db.relationship('Feed', backref=db.backref('user'), lazy='dynamic')


class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(1024))
    hub = db.Column(db.String(255))
    entries = db.relationship('Entry', order_by="Entry.published.desc()", backref=db.backref('feed'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return u'%s' % (self.topic)

    def rss(self):
        items = []
        for entry in self.entries[0:10]:
            items.append(entry.rss())

        rss = rFeed(
        title = self.title,
        link = self.topic,
        description = self.description,
        lastBuildDate = datetime.utcnow(),
        language = "en-US",
        items = items,
        extensions = [
            PushLink(rel='hub', href=self.hub, xmlns='http://www.w3.org/2005/Atom'),
            PushLink(rel='self', href=self.topic, xmlns='http://www.w3.org/2005/Atom')])

        return rss

authors_entries = db.Table('authors_entries',
    db.Column('author_id', db.Integer, db.ForeignKey('author.id')),
    db.Column('entry_id', db.Integer, db.ForeignKey('entry.id')))

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    guid = db.Column(db.String(512))
    published = db.Column(db.DateTime)
    updated = db.Column(db.DateTime)
    content = db.Column(db.Text)
    summary = db.Column(db.Text)
    link = db.Column(db.String(512))
    feed_id = db.Column(db.Integer, db.ForeignKey('feed.id'))
    authors = db.relationship('Author',
        secondary=authors_entries,
        backref=db.backref('entries', lazy='dynamic'))

    def rss(self):
        entry_author = ''
        for author in self.authors:
            entry_author += repr(author) + ', '
        item = Item(
            title = self.title,
            link = self.link,
            description = self.content,
            author = entry_author,
            guid = Guid(self.guid),
            pubDate = self.published)

        return item


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))

    def __repr__(self):
        if self.email:
            return u'%s (%s)' % (self.email, self.name)
        return u'%s' % (self.name)