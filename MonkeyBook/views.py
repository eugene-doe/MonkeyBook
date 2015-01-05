from flask import Flask, session, redirect, url_for, escape, request, render_template, flash
from sqlalchemy import func, and_, desc
from sqlalchemy.orm import aliased
from functools import wraps
from datetime import date
from dateutil import parser
from MonkeyBook import app
from MonkeyBook.models import Monkey, friendship, db
from MonkeyBook.forms import *
import MonkeyBook.dba as dba
import os

## Some views may require two monkey objects: the logged in monkey and some other monkey.
## For the sake of clarity, the logged in monkey is referred to as 'monkey_self' and any
## other monkey (such as a monkey that has not yet logged in or a monkey whose profile we
## are viewing) as 'monkey'.

## All views that expect the user to be logged in should pass monkey_self to the template,
## because monkey_self is used in layout.html.

def login_required(f):
    """Redirect to login page if not logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'id' in session:
            session['next'] = request.url # Because appending next URL to the current one looks ugly
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in to MonkeyBook."""
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        # Find a monkey with a matching email in the database:
        monkey = dba.get_monkey_by_email(form['email'].data)

        # If such monkey is found, compare the password:
        if monkey is not None and monkey.password == form['password'].data:
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
    """Log out of MonkeyBook."""
    # Remove the id from the session if it's there
    session.pop('id', None)
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new monkey."""
    if 'id' in session:
        return redirect(url_for('index'))

    form = ProfileEditForm(request.form)

    if request.method == 'POST' and form.validate():
        # Check for email uniqueness by querying for another monkey with the same address:
        if dba.check_unique_email(form['email'].data):
            # If no duplicate found:
            monkey = dba.register_monkey(form)
            if (monkey):
                # If registered, log in and go to index:
                session['id'] = monkey.id
                return redirect(url_for('index'))
            else:
                flash('Error registering!')
        else:
            form.email.errors.append('This e-mail address is registered with another user')

    return render_template('edit.html', form=form)

@app.route('/delete')
@app.route('/delete/<confirmed>')
@login_required
def delete(confirmed=None):
    """Delete monkey's profile."""
    monkey_self = dba.get_monkey_by_id(session['id'])

    if confirmed == 'confirmed':
        if dba.delete_monkey(monkey_self):
            # If deleted, log out:
            session.pop('id', None)
            flash('Profile deleted')
            return redirect(url_for('index'))
        else:
            flash('Error deleting profile!')
            return redirect(url_for('edit'))
    else:
        return render_template('delete.html', monkey_self=monkey_self)

@app.route('/')
def index():
    """Display the index page, logged in or not."""
    monkey_self = None
    if 'id' in session:
        monkey_self = dba.get_monkey_by_id(session['id'])
    return render_template('index.html', monkey_self=monkey_self)

@app.route('/<int:monkey_id>')
@login_required
def profile(monkey_id):
    """Display a monkey's profile, own or not."""
    monkey_self = dba.get_monkey_by_id(session['id'])

    # This condition avoids running a second query when viewing own profile:
    if monkey_id == session['id']:
        # Viewing your own profile
        monkey = monkey_self
    else:
        # Viewing somebody else's profile
        monkey = dba.get_monkey_by_id(monkey_id)

    if monkey:
        profile = dba.get_monkey_profile(monkey)
    else:
        # Non-existent id in the URL
        return redirect(url_for('index'))

    return render_template('profile.html',
                            monkey=monkey,
                            monkey_self=monkey_self,
                            mutual_friends=profile['mutual_friends'],
                            other_friends=profile['other_friends'],
                            also_friend_of=profile['also_friend_of'])

@app.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    """Edit monkey's own profile."""
    monkey_self = dba.get_monkey_by_id(session['id'])

    # If no formdata is present in the request, the form is populated from the object:
    form = ProfileEditForm(request.form, monkey_self)

    if request.method == 'POST' and form.validate():
        # Check for email uniqueness by querying for another monkey with the same address:
        if dba.check_unique_email(form['email'].data, monkey_self.id):
            # If no duplicate found:
            if dba.edit_monkey_profile(monkey_self, form):
                flash('Changes saved')
            else:
                flash('Error saving changes!')
        else:
            form.email.errors.append('This e-mail address is registered with another user')

    return render_template('edit.html', form=form, monkey_self=monkey_self)

@app.route('/add/<int:monkey_id>')
@login_required
def add(monkey_id):
    """Add a monkey to friends."""
    monkey_self = dba.get_monkey_by_id(session['id'])
    monkey = dba.get_monkey_by_id(monkey_id)
    if not dba.add_friend(monkey_self, monkey):
        flash('Error adding friend!')
    return redirect(request.referrer or url_for('index'))

@app.route('/remove/<int:monkey_id>')
@login_required
def remove(monkey_id):
    """Remove a monkey from friends."""
    monkey_self = dba.get_monkey_by_id(session['id'])
    monkey = dba.get_monkey_by_id(monkey_id)

    # Only a friend can be the best friend:
    if monkey is monkey_self.best_friend:
        if not dba.clear_best_friend(monkey_self):
            flash('Error clearing best friend!')

    if not dba.remove_friend(monkey_self, monkey):
        flash('Error removing friend!')
    return redirect(request.referrer or url_for('index'))

@app.route('/best/<int:monkey_id>')
@login_required
def best(monkey_id):
    """Make a monkey your best friend."""
    monkey_self = dba.get_monkey_by_id(session['id'])
    monkey = dba.get_monkey_by_id(monkey_id)
    if not dba.set_best_friend(monkey_self, monkey):
        flash('Error setting best friend!')
    return redirect(request.referrer or url_for('index'))

@app.route('/clear_best')
@login_required
def clear_best():
    """Clear your best friend."""
    monkey_self = dba.get_monkey_by_id(session['id'])
    if not dba.clear_best_friend(monkey_self):
        flash('Error clearing best friend!')
    return redirect(request.referrer or url_for('index'))

@app.route('/list')
@app.route('/list/<int:page>')
@app.route('/list/<order>')
@app.route('/list/<order>/<int:page>')
@login_required
def list(order=None, page=1):
    """List all monkeys."""
    monkey_self = dba.get_monkey_by_id(session['id'])
    monkeys = dba.list_monkeys(order, page)   
    return render_template('list.html', monkeys=monkeys, monkey_self=monkey_self, order=order)

# Randomly generated secret key
app.secret_key = os.urandom(24)
