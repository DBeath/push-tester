from push_tester import db
from flask.ext.security import UserMixin, RoleMixin

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


class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(1024))
    hub = db.Column(db.String(255))


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
    feed = db.relationship('Feed', backref=db.backref('entries', order_by=id))
    authors = db.relationship('Author',
        secondary=authors_entries,
        backref=db.backref('entries', lazy='dynamic'))


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255))