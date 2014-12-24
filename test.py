# >>> exec(open("test.py").read())

from MonkeyBook.models import db
from MonkeyBook.models import Monkey

db.drop_all()
db.create_all()

jack = Monkey('Jack', '123', 'jack@email.com', '1980-02-03')
jill = Monkey('Jill', '321', 'jill@email.com')
john = Monkey('John', '456', 'john@email.com', '1981-10-19')

jack.friends.append(jill)
jill.friends.append(jack)
jack.friends.append(john)
john.friends.append(jack)
john.friends.append(jill)

jack.bestFriend = jill
john.bestFriend = jack

db.session.add(jack)
db.session.add(jill)
db.session.add(john)
db.session.commit()
