"""
The forms module.
"""

from wtforms import Form, BooleanField, StringField, PasswordField
from wtforms.validators import Email, InputRequired, Length, EqualTo


class LoginForm(Form):
    """The login form."""
    email = StringField(
        'E-mail', [Email(message='Please enter a valid e-mail address')])
    password = PasswordField(
        'Password', [InputRequired(message='Please enter your password')])


class ProfileEditForm(Form):
    """The profile create/edit form."""
    first_name = StringField(
        'First name',
        [Length(min=1, max=80, message='Please enter a valid first name')])
    last_name = StringField(
        'Last name',
        [Length(min=1, max=80, message='Please enter a valid last name')])
    email = StringField(
        'E-mail', [Email(message='Please enter a valid e-mail address')])
    date_of_birth = StringField('Date of birth') # Uses datepicker
    password = PasswordField(
        'Password', [InputRequired(message='Please enter your password'),
                     EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat password')
