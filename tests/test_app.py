"""
The unit test module.
"""

# This module requires database tables to be created, but does not
# require any data to be present.  The database should not contain
# monkeys with the following emails, because they are created during
# the tests: test@email.com, billg@microsoft.com, rms@gnu.org
#
# The tests cover all methods from the database access module.

from datetime import date

import pytest
import sqlalchemy_utils

import MonkeyBook.dba as dba
from MonkeyBook import app
from MonkeyBook.models import Monkey, db
from MonkeyBook.forms import *


@pytest.mark.usefixtures('session')
class TestClass:

    def test_monkey_model(self, session):
        monkey = Monkey('Test', 'User', '123', 'test@email.com',
                        str(date.today()))
        db.session.add(monkey)
        db.session.commit()

        assert monkey.id > 0
        assert monkey.first_name == 'Test'
        assert monkey.last_name == 'User'
        assert type(monkey.password) == \
            sqlalchemy_utils.types.password.Password
        assert monkey.email == 'test@email.com'
        assert monkey.age() == 0

    def test_get_monkey_by_email(self, session):
        monkey = Monkey('Test', 'User', '123', 'test@email.com',
                        str(date.today()))
        db.session.add(monkey)
        db.session.commit()
        
        same_monkey = dba.get_monkey_by_email(monkey.email)

        assert isinstance(same_monkey, Monkey)
        assert same_monkey.email == monkey.email

    def test_get_monkey_by_id(self, session):
        monkey = Monkey('Test', 'User', '123', 'test@email.com',
                        str(date.today()))
        db.session.add(monkey)
        db.session.commit()
        
        same_monkey = dba.get_monkey_by_id(monkey.id)

        assert isinstance(same_monkey, Monkey)
        assert same_monkey.id == monkey.id

    def test_check_unique_email(self, session):
        monkey = Monkey('Test', 'User', '123', 'test@email.com',
                        str(date.today()))
        db.session.add(monkey)
        db.session.commit()

        assert not dba.check_unique_email(monkey.email)
        assert dba.check_unique_email(monkey.email, monkey.id)

    def test_register_monkey(self, session):
        form = ProfileEditForm()
        form['first_name'].data = 'Test'
        form['last_name'].data = 'User'
        form['email'].data = 'test@email.com'
        form['date_of_birth'].data = ''
        form['password'].data = '123'
        form['confirm'].data = '123'

        monkey = dba.register_monkey(form)

        assert isinstance(monkey, Monkey)
        assert monkey.id > 0

    def test_delete_monkey(self, session):
        monkey = Monkey('Test', 'User', '123', 'test@email.com',
                        str(date.today()))
        db.session.add(monkey)
        db.session.commit()

        assert dba.delete_monkey(monkey)

    def test_get_monkey_profile(self, session):
        monkey = Monkey('Test', 'User', '123', 'test@email.com',
                        str(date.today()))
        db.session.add(monkey)
        db.session.commit()

        profile = dba.get_monkey_profile(monkey)

        assert 'mutual_friends' in profile 
        assert 'other_friends' in profile
        assert 'also_friend_of' in profile

    def test_edit_monkey_profile(self, session):
        monkey = Monkey('Test', 'User', '123', 'test@email.com',
                        str(date.today()))
        db.session.add(monkey)
        db.session.commit()

        old_id = monkey.id

        form = ProfileEditForm()
        form['first_name'].data = 'Bill'
        form['last_name'].data = 'Gates'
        form['email'].data = 'billg@microsoft.com'
        form['date_of_birth'].data = ''
        form['password'].data = 'secret'
        form['confirm'].data = 'secret'

        assert dba.edit_monkey_profile(monkey, form)
        assert monkey.id == old_id
        assert monkey.first_name == 'Bill'
        assert monkey.last_name == 'Gates'
        assert type(monkey.password) == \
            sqlalchemy_utils.types.password.Password
        assert monkey.email == 'billg@microsoft.com'
        assert monkey.age() == None

        # Fails to rollback, cleanup:
        dba.delete_monkey(monkey)

    def test_add_friend(self, session):
        bill = Monkey('Bill', 'Gates', 'secret', 'billg@microsoft.com')
        rich = Monkey('Richard', 'Stallman', 'freedom', 'rms@gnu.org')
        db.session.add(bill, rich)
        db.session.commit()

        assert dba.add_friend(rich, bill)
        assert bill in rich.friends
        assert rich in bill.friend_of

        # Fails to rollback, cleanup:
        dba.delete_monkey(bill)
        dba.delete_monkey(rich)

    def test_remove_friend(self, session):
        bill = Monkey('Bill', 'Gates', 'secret', 'billg@microsoft.com')
        rich = Monkey('Richard', 'Stallman', 'freedom', 'rms@gnu.org')
        rich.friends.append(bill)
        db.session.add(bill, rich)
        db.session.commit()

        assert bill in rich.friends
        assert rich in bill.friend_of
        assert dba.remove_friend(rich, bill)
        assert len(list(rich.friends)) == 0
        assert len(list(bill.friend_of)) == 0

        # Fails to rollback, cleanup:
        dba.delete_monkey(bill)
        dba.delete_monkey(rich)

    def test_set_best_friend(self, session):
        bill = Monkey('Bill', 'Gates', 'secret', 'billg@microsoft.com')
        rich = Monkey('Richard', 'Stallman', 'freedom', 'rms@gnu.org')
        rich.friends.append(bill)
        db.session.add(bill, rich)
        db.session.commit()

        assert dba.set_best_friend(rich, bill)
        assert rich.best_friend is bill
        assert rich.best_friend_id == bill.id

        # Fails to rollback, cleanup:
        dba.delete_monkey(bill)
        dba.delete_monkey(rich)

    def test_clear_best_friend(self, session):
        bill = Monkey('Bill', 'Gates', 'secret', 'billg@microsoft.com')
        rich = Monkey('Richard', 'Stallman', 'freedom', 'rms@gnu.org')
        rich.friends.append(bill)
        rich.best_friend = bill
        db.session.add(bill, rich)
        db.session.commit()

        assert dba.clear_best_friend(rich)
        assert rich.best_friend == None
        assert rich.best_friend_id == None

        # Fails to rollback, cleanup:
        dba.delete_monkey(bill)
        dba.delete_monkey(rich)

    def test_list_monkeys(self, session):
        monkeys = dba.list_monkeys()

        assert monkeys.has_prev is not None
        assert monkeys.has_next is not None
        assert monkeys.iter_pages() is not None
        assert monkeys.page is not None
