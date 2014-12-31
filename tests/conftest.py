from MonkeyBook.models import db
import pytest

# This does not work quite as desired and requires some additional cleanup in the tests.
# To be improved (as soon as I find a clean and elegant way to achieve the desired result).

@pytest.yield_fixture(scope='function')
def session():
    """Begin a nested session to roll back the transaction once it is over."""
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
