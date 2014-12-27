from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils.types.password import PasswordType
from datetime import date
from dateutil import parser

db = SQLAlchemy()

friendship = db.Table('friendship',
    db.Column('left_monkey_id', db.Integer, db.ForeignKey('monkey.id'), primary_key=True),
    db.Column('right_monkey_id', db.Integer, db.ForeignKey('monkey.id'), primary_key=True))

class Monkey(db.Model):
    __tablename__ = 'monkey' # optional in Flask-SQLAlchemy, but included for clarity

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512', 'md5_crypt'], deprecated=['md5_crypt']), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)

    best_friend_id = db.Column(db.Integer, db.ForeignKey('monkey.id', ondelete='SET NULL'))
    best_friend = db.relationship('Monkey', uselist=False, remote_side=[id], post_update=True, lazy='joined')

    friends = db.relationship('Monkey',
                        secondary=friendship,
                        primaryjoin=id == friendship.c.left_monkey_id,
                        secondaryjoin=id == friendship.c.right_monkey_id,
                        backref=db.backref('friend_of', lazy='dynamic'))
    
    def __init__(self, first_name, last_name, password, email, date_of_birth=None):
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.email = email
        if date_of_birth: self.date_of_birth = date_of_birth # False if None or empty string

    def age(self):
        """Calculate monkey's age from date of birth."""
        # date_of_birth is a string before commit and a date object afterwards, therefore:
        if self.date_of_birth:
            if type(self.date_of_birth) is str:
                try:
                    bdate = parser.parse(self.date_of_birth).date()
                except Exception:
                    # If age() is called on an unbound monkey with incorrect date of birth, no age is returned:
                    return None
            else:
                bdate = self.date_of_birth
            today = date.today()
            return today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))

    def __repr__(self):
        if self.age():
            return '{0} {1} ({2})'.format(self.first_name, self.last_name, self.age())
        else:
            return '{0} {1}'.format(self.first_name, self.last_name)
