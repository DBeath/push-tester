from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField, validators, \
    SelectMultipleField
from wtforms.fields.html5 import DateField, DateTimeField

class AuthorForm(Form):
    name = StringField(u'Author', validators=[validators.InputRequired()])
    email = StringField(u'Email', validators=[validators.Optional(), validators.Email()])


class FeedForm(Form):
    topic = StringField(u'Topic', validators=[validators.InputRequired(), validators.URL()])
    description = StringField(u'Description', validators=[validators.Optional()])
    hub = StringField(u'Hub', validators=[validators.Optional(), validators.URL()])


class EntryForm(Form):
    title = StringField(u'Title', validators=[validators.Optional()])
    guid = StringField(u'Guid', validators=[validators.Optional()])
    published = DateTimeField(u'Published', validators=[validators.InputRequired()])
    updated = DateField(u'Updated', validators=[validators.Optional()])
    content = TextAreaField(u'Content', validators=[validators.Optional()])
    summary = TextAreaField(u'Summary', validators=[validators.Optional()])
    link = StringField(u'Link', validators=[validators.InputRequired()])
    feed = SelectField(u'Feed', validators=[validators.InputRequired()])
    authors = SelectMultipleField('Authors', validators=[validators.Optional()])