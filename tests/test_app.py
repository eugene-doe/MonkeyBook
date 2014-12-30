from MonkeyBook.models import Monkey, db
from datetime import date

def test_monkey_model(session):
    """Test monkey creation."""
    test_monkey = Monkey('Test', 'User', '123', 'test@email.com', str(date.today()))

    db.session.add(test_monkey)
    db.session.commit()

    assert test_monkey.id > 0

def test_monkey_age(session):
    """Test monkey age calculation."""
    test_monkey = Monkey('Test', 'User', '123', 'test@email.com', str(date.today()))

    db.session.add(test_monkey)
    db.session.commit()

    assert test_monkey.age()== 0
