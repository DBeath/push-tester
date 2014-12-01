from flask.ext.wtf import Form
from wtforms import TextField
from wtforms.validators import InputRequired

class AuthorForm(Form):
    name = TextField('Author', validators=[InputRequired()])
    email = TextField('Email', validators=[])