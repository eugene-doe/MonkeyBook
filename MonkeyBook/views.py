from flask import Flask, session, redirect, url_for, escape, request, render_template
from sqlalchemy import func
from MonkeyBook import app
from MonkeyBook.models import Monkey
from MonkeyBook.forms import LoginForm
import os

@app.route('/')
def index():
    if 'email' in session:
        monkey = Monkey.query.filter_by(email = session['email']).first()

        # The following lists keep logic out of the templates
        # and keep the model simple at the same time:

        mutual_friends = set(monkey.friends).intersection(monkey.friend_of)
        other_friends = set(monkey.friends).difference(monkey.friend_of)
        also_friend_of = set(monkey.friend_of).difference(monkey.friends)

        return render_template('profile.html',
                               monkey=monkey,
                               mutual_friends=mutual_friends,
                               other_friends=other_friends,
                               also_friend_of=also_friend_of)
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        # Find a monkey with a matching email in the database:
        monkey = Monkey.query.filter(func.lower(Monkey.email) == func.lower(request.form['email'])).first()

        # If such monkey is found, compare the password:
        if monkey is not None and monkey.password == request.form['password']:
            # If matches, log in:
            session['email'] = monkey.email
        else:
            # Assuming that we don't want the user to know which part of the input was wrong:
            form.email.errors.append('Invalid e-mail address or password')

    # If logged in, redirect to index, othwerwise show login form:
    if 'email' in session:
        return redirect(url_for('index'))
    else: 
        return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    # Remove the email from the session if it's there
    session.pop('email', None)
    return redirect(url_for('index'))

# Randomly generated secret key
app.secret_key = os.urandom(24)
