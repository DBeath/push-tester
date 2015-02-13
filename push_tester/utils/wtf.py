# Helpers for form generation
from wtforms.fields import HiddenField, BooleanField
from wtforms.ext.dateutil.fields import DateTimeField


def add_helpers(app):
    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)

    def is_boolean_field_filter(field):
        return isinstance(field, BooleanField)

    def is_datetime_field_filter(field):
        return isinstance(field, DateTimeField)

    app.jinja_env.filters['is_hidden_field'] = is_hidden_field_filter
    app.jinja_env.filters['is_boolean_field'] = is_boolean_field_filter
    app.jinja_env.filters['is_datetime_field'] = is_datetime_field_filter
