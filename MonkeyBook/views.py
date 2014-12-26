from flask import Flask, session, redirect, url_for, escape, request, render_template
from sqlalchemy import func, and_
from functools import wraps
from datetime import date
from dateutil import parser
from MonkeyBook import app
from MonkeyBook.models import Monkey
from MonkeyBook.forms import *
from MonkeyBook.models import db
import os

## Some views may require two monkey objects: the logged in monkey and some other monkey.
## For the sake of clarity, the logged in monkey is referred to as 'monkey_self' and any
## other monkey (such as a monkey that has not yet logged in or a monkey whose profile we
## are viewing) as 'monkey'.

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'id' in session:
            session['next'] = request.url # Because appending next URL to the current one looks ugly
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        # Find a monkey with a matching email in the database:
        monkey = Monkey.query.filter(func.lower(Monkey.email) == func.lower(request.form['email'])).first()

        # If such monkey is found, compare the password:
        if monkey is not None and monkey.password == request.form['password']:
            # If matches, log in:
            next = session.get('next')
            session.clear()
            session['id'] = monkey.id
        else:
            # Assuming that we don't want the user to know which part of the input was wrong:
            form.email.errors.append('Invalid e-mail address or password')

    # If logged in, redirect to index, othwerwise show login form:
    if 'id' in session:
        return redirect(next or url_for('index'))
    else:
        return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    # Remove the id from the session if it's there
    session.pop('id', None)
    return redirect(url_for('index'))

@app.route('/')
def index():
    monkey_self = None
    if 'id' in session:
        monkey_self = Monkey.query.filter_by(id = session['id']).first()
    return render_template('index.html', monkey_self=monkey_self)

@app.route('/<int:monkey_id>')
@login_required
def profile(monkey_id):
    monkey_self = Monkey.query.filter_by(id = session['id']).first()

    if monkey_id == session['id']:
        # Viewing your own profile
        monkey = monkey_self
    else:
        # Viewing somebody else's profile
        monkey = Monkey.query.filter_by(id = monkey_id).first()

    # The following lists keep logic out of the templates
    # and keep the model simple at the same time:

    mutual_friends = set(monkey.friends).intersection(monkey.friend_of)
    other_friends = set(monkey.friends).difference(monkey.friend_of)
    also_friend_of = set(monkey.friend_of).difference(monkey.friends)

    return render_template('profile.html',
                            monkey=monkey,
                            monkey_self=monkey_self,
                            mutual_friends=mutual_friends,
                            other_friends=other_friends,
                            also_friend_of=also_friend_of)

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    monkey_self = Monkey.query.filter_by(id = session['id']).first()

    # If no formdata is present in the request, the form is populated from the object:
    form = ProfileEditForm(request.form, monkey_self)

    # Used in the template:
    edit_result = ''
    edit_result_class = ''

    if request.method == 'POST' and form.validate():
        # Check for email uniqueness by querying for another monkey with the same address:
        if not Monkey.query.filter(and_(func.lower(Monkey.email) == func.lower(request.form['email']),
                                        Monkey.id != session['id'])).first():
            # If no duplicate found, populate the monkey object and commit:
            form.populate_obj(monkey_self)

            try:
                if monkey_self.date_of_birth == '':
                    # Handling empty birth dates:
                    monkey_self.date_of_birth = None
                else:
                    # Handling different date formats:
                    monkey_self.date_of_birth = parser.parse(request.form['date_of_birth']).date()
                db.session.commit()
                edit_result = 'Changed saved'
                edit_result_class = 'message_ok'
            except Exception:
                db.session.close()
                edit_result = 'Error saving changes'
                edit_result_class = 'message_error'
        else:
            form.email.errors.append('This e-mail address is registered with another user')

    return render_template('edit.html',
                           form=form,
                           monkey_self=monkey_self,
                           edit_result=edit_result,
                           edit_result_class=edit_result_class)

# Randomly generated secret key
app.secret_key = os.urandom(24)
