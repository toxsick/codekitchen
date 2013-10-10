#forms.py
from cyclone_wtforms.forms import Form
from wtforms import validators
import wtforms


class ExampleForm(Form):
    title = wtforms.TextField(u'Title', validators=[validators.Required("Title missing!")])
    content = wtforms.TextAreaField(u'Content', validators=[validators.Required("Content missing!")])
    #hallo = wtforms.TextAreaField(u'Hallo', validators=[validators.Required()])
    #image = wtforms.FileField(u'Image File', validators=[validators.Required()])
