from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField, validators, \
    SelectMultipleField, FieldList, BooleanField
from wtforms.fields.html5 import DateField, DateTimeField

class AuthorForm(Form):
    name = StringField(u'Author', validators=[validators.InputRequired()])
    email = StringField(u'Email', validators=[validators.Optional(), validators.Email()])


class FeedForm(Form):
    title = StringField(u'Title', validators=[validators.Optional()])
    description = StringField(u'Description', validators=[validators.Optional()])
    hub = StringField(u'Hub', validators=[validators.Optional(), validators.URL()])


class EntryForm(Form):
    title = StringField(u'Title', validators=[validators.Optional()])
    published = DateTimeField(u'Published', validators=[validators.Optional()])
    updated = DateField(u'Updated', validators=[validators.Optional()])
    content = TextAreaField(u'Content', validators=[validators.Optional()])
    summary = TextAreaField(u'Summary', validators=[validators.Optional()])
    feed = SelectField(u'Feed', validators=[validators.InputRequired()], coerce=int)
    authors = SelectMultipleField(u'Authors', validators=[validators.Optional()], coerce=int)
    ping = BooleanField(u'Ping Hub')