from wtforms import Form, BooleanField, StringField, PasswordField, validators

class LoginForm(Form):
    email = StringField('E-mail', [validators.Email(message='Please enter a valid e-mail address')])
    password = PasswordField('Password', [validators.Length(min=1, max=80, message='Please enter a password')])
