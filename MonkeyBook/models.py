from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils.types.password import PasswordType
from datetime import date

db = SQLAlchemy()

friendship = db.Table('friendship',
    db.Column('left_monkey_id', db.Integer, db.ForeignKey('monkey.id'), primary_key=True),
    db.Column('right_monkey_id', db.Integer, db.ForeignKey('monkey.id'), primary_key=True))

class Monkey(db.Model):
    __tablename__ = 'monkey' # optional in Flask-SQLAlchemy, but included for clarity

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512', 'md5_crypt'], deprecated=['md5_crypt']))
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)

    best_friend_id = db.Column(db.Integer, db.ForeignKey('monkey.id', ondelete='SET NULL'))
    bestFriend = db.relationship('Monkey', uselist=False, remote_side=[id])

    friends = db.relationship('Monkey',
                        secondary=friendship,
                        primaryjoin=id == friendship.c.left_monkey_id,
                        secondaryjoin=id == friendship.c.right_monkey_id,
                        backref='friend_of') # backref=db.backref('friendOf', lazy='dynamic') for large collections
    
    def __init__(self, name, password, email, date_of_birth=None):
        self.name = name
        self.password = password
        self.email = email
        if date_of_birth is not None: self.date_of_birth = date_of_birth

    def age(self):
        if self.date_of_birth is not None:
            bdate = self.date_of_birth
            today = date.today()
            return today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
        else:
            return None

    def __repr__(self):
        if self.age() is not None:
            return '{0} ({1})'.format(self.name, self.age())
        else:
            return '{0}'.format(self.name)
