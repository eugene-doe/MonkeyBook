from wtforms import Form, BooleanField, StringField, PasswordField
from wtforms.validators import *

class LoginForm(Form):
    email = StringField('E-mail', [Email(message='Please enter a valid e-mail address')])
    password = PasswordField('Password', [InputRequired(message='Please enter your password')])

class ProfileEditForm(Form):
    first_name = StringField('First name', [Length(min=1, max=80, message='Please enter a valid e-mail address')])
    last_name = StringField('Last name', [Length(min=1, max=80, message='Please enter a valid e-mail address')])
    email = StringField('E-mail', [Email(message='Please enter a valid e-mail address')])
    date_of_birth = StringField('Date of birth') # Datepicker needed
    password = PasswordField('Password', [InputRequired(message='Please enter your password'),
                                          EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat Password')
