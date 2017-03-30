from flask_wtf import Form
from wtforms.fields import StringField, SubmitField, PasswordField
from wtforms.validators import Required


class LoginForm(Form):
    """Accepts a nickname and a room."""
    email = StringField('E-mail', validators=[Required()])
    pw = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Login')

class SignupForm(Form):
    """Accepts a nickname and a room."""
    email2 = StringField('E-mail', validators=[Required()])
    pw2 = PasswordField('Password', validators=[Required()])
    submit2 = SubmitField('Create Acount')

class TwitterForm(Form):
    """Accepts a nickname and a room."""
    twiid = StringField('Twitter ID', validators=[Required()])
    twipw = PasswordField('Password', validators=[Required()])
    submit3 = SubmitField('Login')

class ConfigForm(Form):
    """Accepts a nickname and a room."""
    email4 = StringField('E-mail', validators=[Required()])
    pw4 = PasswordField('Password', validators=[Required()])
    submit4 = SubmitField('Config')
