"""
The models test module.
"""

# This module requires database tables to be created, but does not
# require any data to be present.  If the database contains monkeys
# with the following emails, they will be deleted before testing:
# test@email.com, billg@microsoft.com, rms@gnu.org
#
# The tests cover all methods from the database access module.

from datetime import date

import pytest
import sqlalchemy_utils

import MonkeyBook.dba as dba
from MonkeyBook.models import Monkey, db
from MonkeyBook.forms import LoginForm, ProfileEditForm


@pytest.mark.usefixtures('cleanup')
class TestModels:

    def test_monkey_model(self, test_monkey):
        """Test monkey model."""
        monkey = test_monkey
        assert monkey.id > 0
        assert monkey.first_name == 'Test'
        assert monkey.last_name == 'User'
        assert type(monkey.password) == \
            sqlalchemy_utils.types.password.Password
        assert monkey.email == 'test@email.com'
        assert monkey.age() == 0

    def test_get_monkey_by_email(self, test_monkey):
        """Test get_monkey_by_email()."""
        monkey = test_monkey
        same_monkey = dba.get_monkey_by_email(monkey.email)
        assert isinstance(same_monkey, Monkey)
        assert same_monkey.email == monkey.email

    def test_get_monkey_by_id(self, test_monkey):
        """Test get_monkey_by_id()."""
        monkey = test_monkey
        same_monkey = dba.get_monkey_by_id(monkey.id)
        assert isinstance(same_monkey, Monkey)
        assert same_monkey.id == monkey.id

    def test_check_unique_email(self, test_monkey):
        """Test check_unique_email()."""
        monkey = test_monkey
        assert not dba.check_unique_email(monkey.email)
        assert dba.check_unique_email(monkey.email, monkey.id)

    def test_register_monkey(self):
        """Test register_monkey()."""
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

    def test_delete_monkey(self, test_monkey):
        """Test delete_monkey()."""
        monkey = test_monkey
        assert dba.delete_monkey(monkey)

    def test_get_monkey_profile(self, test_monkey):
        """Test get_monkey_profile()."""
        monkey = test_monkey
        profile = dba.get_monkey_profile(monkey)
        assert 'mutual_friends' in profile 
        assert 'other_friends' in profile
        assert 'also_friend_of' in profile

    def test_edit_monkey_profile(self, test_monkey):
        """Test edit_monkey_profile()."""
        monkey = test_monkey
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
        assert monkey.age() is None

    def test_add_friend(self, test_friends):
        """Test add_friend()."""
        bill = test_friends[0]
        rich = test_friends[1]
        assert dba.add_friend(rich, bill)
        assert bill in rich.friends
        assert rich in bill.friend_of

    def test_add_friend_none(self, test_monkey):
        """Test add_friend() with None values."""
        bill = None
        rich = None
        assert not dba.add_friend(rich, bill)

        bill = test_monkey
        rich = None
        assert not dba.add_friend(rich, bill)

        bill = None
        rich = test_monkey
        assert not dba.add_friend(rich, bill)

    def test_remove_friend(self, test_friends):
        """Test remove_friend()."""
        bill = test_friends[0]
        rich = test_friends[1]
        rich.friends.append(bill)
        assert bill in rich.friends
        assert rich in bill.friend_of
        assert dba.remove_friend(rich, bill)
        assert len(list(rich.friends)) == 0
        assert len(list(bill.friend_of)) == 0

    def test_remove_friend_none(self, test_monkey):
        """Test remove_friend() with None values."""
        bill = None
        rich = None
        assert not dba.remove_friend(rich, bill)

        bill = test_monkey
        rich = None
        assert not dba.remove_friend(rich, bill)

        bill = None
        rich = test_monkey
        assert not dba.remove_friend(rich, bill)

    def test_set_best_friend(self, test_friends):
        """Test set_best_friend()."""
        bill = test_friends[0]
        rich = test_friends[1]
        rich.friends.append(bill)
        assert dba.set_best_friend(rich, bill)
        assert rich.best_friend is bill
        assert rich.best_friend_id == bill.id

    def test_set_best_friend_none(self, test_monkey):
        """Test set_best_friend() with None values."""
        bill = None
        rich = None
        assert not dba.set_best_friend(rich, bill)

        bill = test_monkey
        rich = None
        assert not dba.set_best_friend(rich, bill)

        bill = None
        rich = test_monkey
        assert not dba.set_best_friend(rich, bill)

    def test_clear_best_friend(self, test_friends):
        """Test clear_best_friend()."""
        bill = test_friends[0]
        rich = test_friends[1]
        rich.friends.append(bill)
        rich.best_friend = bill
        assert dba.clear_best_friend(rich)
        assert rich.best_friend is None
        assert rich.best_friend_id is None

    def test_clear_best_friend_none(self):
        """Test clear_best_friend() with None values."""
        monkey = None
        assert not dba.clear_best_friend(monkey)

    def test_list_monkeys(self):
        """Test list_monkeys()."""
        monkeys = dba.list_monkeys()
        assert monkeys.has_prev is not None
        assert monkeys.has_next is not None
        assert monkeys.iter_pages() is not None
        assert monkeys.page is not None
