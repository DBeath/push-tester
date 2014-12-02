from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import InputRequired

class AuthorForm(Form):
    name = TextField('Author', validators=[InputRequired()])
    email = TextField('Email', validators=[])


class FeedForm(Form):
    topic = TextField('Topic', validators=[InputRequired()])
    description = TextField('Description', validators=[])
    hub = TextField('Hub', validators=[])