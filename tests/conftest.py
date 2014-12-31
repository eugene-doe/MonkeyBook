from MonkeyBook.models import db
import pytest

@pytest.yield_fixture(scope='function')
def session():
    """Begin a nested session to roll back the transaction once it is over."""
    db.session.begin_nested()
    yield db.session
    db.session.rollback()
