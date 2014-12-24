from flask import Flask, session, redirect, url_for, escape, request, render_template
from sqlalchemy import func
from MonkeyBook import app
from MonkeyBook.models import Monkey
from MonkeyBook.forms import LoginForm
import os

@app.route('/')
def index():
    if 'name' in session:
        return 'Logged in as %s' % escape(session['name'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        # Find a monkey with a matching name in the database:
        monkey = Monkey.query.filter(func.lower(Monkey.name) == func.lower(request.form['name'])).first()

        # If such monkey is found, compare the password:
        if monkey is not None and monkey.password == request.form['password']:
            # If matches, log in:
            session['name'] = monkey.name
        else:
            # Assuming that we don't want the user to know which part of the input was wrong:
            form.name.errors.append('Invalid name or password')

    # If logged in, redirect to index, othwerwise show login form:
    if 'name' in session:
        return redirect(url_for('index'))
    else: 
        return render_template('login.html', form = form)

@app.route('/logout')
def logout():
    # Remove the name from the session if it's there
    session.pop('name', None)
    return redirect(url_for('index'))

# Randomly generated secret key
app.secret_key = os.urandom(24)
