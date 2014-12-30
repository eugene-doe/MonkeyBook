# >>> exec(open("db_initial.py").read())

from MonkeyBook.models import db
from MonkeyBook.models import Monkey

db.drop_all()
db.create_all()

jack = Monkey('Jack', 'Jones', '123', 'jack@email.com', '1980-02-03')
jill = Monkey('Jill', 'Jones','321', 'jill@email.com')
john = Monkey('John', 'Doe', '456', 'john@email.com', '1981-10-19')

db.session.add(jack)
db.session.add(jill)
db.session.add(john)

jill.friends.append(jack)
jack.friends.append(jill)
jack.friends.append(john)
john.friends.append(jack)
john.friends.append(jill)

jack.best_friend = jill
john.best_friend = jack

db.session.commit()
