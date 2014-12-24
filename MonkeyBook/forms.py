from wtforms import Form, BooleanField, StringField, PasswordField, validators

class LoginForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=80, message='Please enter your name')])
    password = PasswordField('Password')
