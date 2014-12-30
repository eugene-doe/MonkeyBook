from MonkeyBook import app
from MonkeyBook.models import Monkey, db
from datetime import date
import pytest, sqlalchemy_utils

class TestClass:

    @pytest.mark.usefixtures('session')
    def test_monkey_model(session):
        monkey = Monkey('Test', 'User', '123', 'test@email.com', str(date.today()))
        
        db.session.add(monkey)
        db.session.commit()

        assert monkey.id > 0
        assert monkey.first_name == 'Test'
        assert monkey.last_name == 'User'
        assert type(monkey.password) == sqlalchemy_utils.types.password.Password
        assert monkey.email == 'test@email.com'
        assert monkey.age() == 0
