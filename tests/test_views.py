"""
The views test module.
"""

import pytest

from flask import url_for

from MonkeyBook.models import Monkey


@pytest.mark.usefixtures('cleanup')
class TestViews:

    # Helper methods:

    def login(self, app, email, password):
        """Log in to the app."""
        return app.post('/login', data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self, app):
        """Log out of the app."""
        return app.get('/logout', follow_redirects=True)

    def register(self, app, first_name, last_name, email,
                        date_of_birth, password, confirm):
        """Register a new monkey."""
        return app.post('/register', data=dict(
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=date_of_birth,
            password=password,
            confirm=confirm
        ), follow_redirects=True)

    def edit(self, app, first_name, last_name, email,
                        date_of_birth, password, confirm):
        """Edit monkey's profile."""
        return app.post('/edit', data=dict(
            first_name=first_name,
            last_name=last_name,
            email=email,
            date_of_birth=date_of_birth,
            password=password,
            confirm=confirm
        ), follow_redirects=True)

    # Test methods:

    def test_index(self, app):
        """Test index view."""
        assert url_for('index') == '/'

        rv = app.get('/')
        data_string = str(rv.data, encoding='utf8')
        assert 'Monkeybook' in data_string
        assert rv.status_code == 200

    def test_login_logout(self, app, test_monkey):
        """Test login and logout."""
        assert url_for('login') == '/login'
        assert url_for('logout') == '/logout'

        rv = self.login(app, 'test@email.com', '123')
        data_string = str(rv.data, encoding='utf8')
        assert 'Log out' in data_string
        assert rv.status_code == 200

        rv = self.logout(app)
        data_string = str(rv.data, encoding='utf8')
        assert 'Log in' in data_string
        assert rv.status_code == 200

        rv = self.login(app, 'billg@microsoft.com', '123')
        data_string = str(rv.data, encoding='utf8')
        assert 'Invalid' in data_string
        assert rv.status_code == 200

        rv = self.login(app, 'test@', '')
        data_string = str(rv.data, encoding='utf8')
        assert 'Please enter a valid e-mail address' in data_string
        assert 'Please enter your password' in data_string
        assert rv.status_code == 200

    def test_register(self, app):
        """Test successful registration."""
        assert url_for('register') == '/register'

        rv = self.register(app, 'Test', 'User', 'test@email.com', '',
                           '123', '123')
        data_string = str(rv.data, encoding='utf8')
        assert 'Log out' in data_string
        assert rv.status_code == 200

        # Log out returns to initial state
        self.logout(app)

    def test_register_errors(self, app):
        """Test registration errors."""
        rv = self.register(app, 'Test', 'User', 'test@email.com', '',
                           '123', '')
        data_string = str(rv.data, encoding='utf8')
        assert 'Passwords must match' in data_string
        assert rv.status_code == 200

        rv = self.register(app, '', '', '', '', '', '')
        data_string = str(rv.data, encoding='utf8')
        assert 'Please enter a valid e-mail address' in data_string
        assert 'Please enter a valid first name' in data_string
        assert 'Please enter a valid last name' in data_string
        assert 'Please enter your password' in data_string
        assert rv.status_code == 200

    def test_delete(self, app, test_monkey):
        """Test profile deletion."""
        assert url_for('delete') == '/delete'
        assert url_for('delete', confirmed='confirmed') == '/delete/confirmed'

        # Must log in first
        self.login(app, 'test@email.com', '123')
        rv = app.get('/delete/confirmed', follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'Profile deleted' in data_string
        assert rv.status_code == 200

    def test_edit(self, app, test_monkey):
        """Test profile editing."""
        assert url_for('edit') == '/edit'

        # Must log in first
        self.login(app, 'test@email.com', '123')
        rv = self.edit(app, 'New', 'Name', 'test@email.com', '',
                           '123', '123')
        data_string = str(rv.data, encoding='utf8')
        assert 'New Name' in data_string
        assert 'Changes saved' in data_string
        assert rv.status_code == 200

    def test_edit_date_error(self, app, test_monkey):
        """Test profile editing with incorrect date."""
        # Must log in first
        self.login(app, 'test@email.com', '123')
        rv = self.edit(app, 'New', 'Name', 'test@email.com', 'blah',
                           '123', '123')
        data_string = str(rv.data, encoding='utf8')
        assert 'Test User' in data_string
        assert 'Error saving changes!' in data_string
        assert 'Incorrect date format' in data_string
        assert rv.status_code == 200

    def test_profile(self, app, test_monkey):
        """Test profile page."""
        assert url_for('profile',
                       monkey_id=test_monkey.id) == '/' + str(test_monkey.id)

        # Must log in first
        self.login(app, 'test@email.com', '123')
        rv = app.get('/' + str(test_monkey.id), follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'That\'s you' in data_string
        assert rv.status_code == 200

    def test_friendship(self, app, test_monkey, test_bill):
        """Test friendship."""
        assert url_for('add',
                       monkey_id=test_bill.id) == '/add/' + str(test_bill.id)
        assert url_for('remove',
                       monkey_id=test_bill.id) == '/remove/' + \
                           str(test_bill.id)

        # Must log in first
        self.login(app, 'test@email.com', '123')
        app.get('/add/' + str(test_bill.id), follow_redirects=True)
        rv = app.get('/' + str(test_bill.id), follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'Bill Gates is your friend' in data_string
        assert rv.status_code == 200

        app.get('/remove/' + str(test_bill.id), follow_redirects=True)
        rv = app.get('/' + str(test_bill.id), follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'Bill Gates is not your friend' in data_string
        assert rv.status_code == 200

    def test_best_friend(self, app, test_monkey, test_bill):
        """Test best friend."""
        assert url_for('best',
                       monkey_id=test_bill.id) == '/best/' + str(test_bill.id)
        assert url_for('clear_best') == '/clear_best'

        # Must log in first
        self.login(app, 'test@email.com', '123')
        app.get('/best/' + str(test_bill.id), follow_redirects=True)
        rv = app.get('/' + str(test_bill.id), follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'Bill Gates is your best friend' in data_string
        assert rv.status_code == 200

        app.get('/clear_best', follow_redirects=True)
        rv = app.get('/' + str(test_monkey.id), follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'You have not chosen a best friend yet' in data_string
        assert rv.status_code == 200

    def test_monkey_list(self, app, test_monkey):
        """Test monkey list."""
        assert url_for('list', order=None, page=None) == '/list'
        assert url_for('list', order=None, page=1) == '/list/1'
        assert url_for('list',
                       order='best_friend',
                       page=None) == '/list/best_friend'
        assert url_for('list',
                       order='best_friend',
                       page=1) == '/list/best_friend/1'
        assert url_for('list', order='friends', page=None) == '/list/friends'
        assert url_for('list', order='friends', page=1) == '/list/friends/1'

        # Must log in first
        self.login(app, 'test@email.com', '123')
        rv = app.get('/list', follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'All monkeys' in data_string
        assert rv.status_code == 200

        rv = app.get('/list/1', follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'All monkeys' in data_string
        assert rv.status_code == 200

        rv = app.get('/list/best_friend', follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'All monkeys' in data_string
        assert rv.status_code == 200

        rv = app.get('/list/best_friend/1', follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'All monkeys' in data_string
        assert rv.status_code == 200

        rv = app.get('/list/friends', follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'All monkeys' in data_string
        assert rv.status_code == 200
        
        rv = app.get('/list/friends/1', follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'All monkeys' in data_string
        assert rv.status_code == 200

        rv = app.get('/list/nonsense', follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'All monkeys' in data_string
        assert rv.status_code == 200
        
        rv = app.get('/list/0', follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'All monkeys' in data_string
        assert rv.status_code == 200

        rv = app.get('/list/nonsense/1', follow_redirects=True)
        data_string = str(rv.data, encoding='utf8')
        assert 'All monkeys' in data_string
        assert rv.status_code == 200
