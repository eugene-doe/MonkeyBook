"""
The test configuration module.
"""

from datetime import date

from sqlalchemy import func, and_, desc
import pytest

from MonkeyBook.models import Monkey, db
import MonkeyBook


@pytest.fixture(scope='module')
def app(request):
    """Set up the test client."""
    app = MonkeyBook.app
    app_context = app.app_context()
    req_context = app.test_request_context()
    app_context.push()
    req_context.push()

    def fin():
        app_context.pop()
        req_context.pop()

    request.addfinalizer(fin)
    return app.test_client()


@pytest.fixture
def cleanup():
    """Delete the test users that may be left over."""
    old_monkey = Monkey.query.filter(
        func.lower(Monkey.email) == 'test@email.com').first()
    old_bill = Monkey.query.filter(
        func.lower(Monkey.email) == 'billg@microsoft.com').first()
    old_rich = Monkey.query.filter(
        func.lower(Monkey.email) == 'rms@gnu.org').first()

    if old_monkey:
        db.session.delete(old_monkey)
    if old_bill:
        db.session.delete(old_bill)
    if old_rich:
        db.session.delete(old_rich)

    if old_monkey or old_bill or old_rich:
        db.session.commit()


@pytest.fixture
def test_monkey(request):
    """Create a test monkey."""
    monkey = Monkey('Test', 'User', '123', 'test@email.com', str(date.today()))
    db.session.add(monkey)
    db.session.commit()

    def fin():
        db.session.delete(monkey)
        db.session.commit()

    request.addfinalizer(fin)
    return monkey


@pytest.fixture
def test_friends(request):
    """Create two test monkeys for friendship tests."""
    bill = Monkey('Bill', 'Gates', 'secret', 'billg@microsoft.com')
    rich = Monkey('Richard', 'Stallman', 'freedom', 'rms@gnu.org')
    db.session.add(bill, rich)
    db.session.commit()

    def fin():
        db.session.delete(bill)
        db.session.delete(rich)
        db.session.commit()

    request.addfinalizer(fin)
    return [bill, rich]


@pytest.fixture
def test_bill(request):
    """Create one additional monkey for friendship tests."""
    bill = Monkey('Bill', 'Gates', 'secret', 'billg@microsoft.com')
    db.session.add(bill)
    db.session.commit()

    def fin():
        db.session.delete(bill)
        db.session.commit()

    request.addfinalizer(fin)
    return bill
