"""
The database access module.
"""

from sqlalchemy import func, and_, desc
from sqlalchemy.orm import aliased
from datetime import date
from dateutil import parser
from MonkeyBook import app
from MonkeyBook.models import Monkey, friendship, db
from MonkeyBook.forms import *

def get_monkey_by_email(email):
    """Get monkey by email."""
    return Monkey.query.filter(func.lower(Monkey.email) == func.lower(email)).first()

def get_monkey_by_id(id):
    """Get monkey by id."""
    return Monkey.query.get(id)

def check_unique_email(email, id=None):
    """Check that the email does not belong to anybody but the given id."""
    if id:
        return (Monkey.query.filter(and_(func.lower(Monkey.email) == func.lower(email), Monkey.id != id)).first() == None)
    else:
        return (Monkey.query.filter(func.lower(Monkey.email) == func.lower(email)).first() == None)

def register_monkey(form):
    """Register a new monkey."""
    # Create a monkey object from the form:
    monkey = Monkey(form['first_name'].data,
                    form['last_name'].data,
                    form['password'].data,
                    form['email'].data)

    try:
        if form['date_of_birth'].data == '':
            # Handling empty birth dates:
            monkey.date_of_birth = None
        else:
            # Handling different date formats:
            monkey.date_of_birth = parser.parse(form['date_of_birth'].data).date()
        db.session.add(monkey)
        db.session.commit()
        return monkey
    except Exception as e:
        if type(e) is ValueError:
            form.date_of_birth.errors.append('Incorrect date format')
        db.session.rollback()
        return None

def delete_monkey(monkey):
    """Delete monkey's profile."""
    db.session.delete(monkey)
    try:
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def get_monkey_profile(monkey):
    mutual_friends = set(monkey.friends).intersection(monkey.friend_of)
    other_friends  = set(monkey.friends).difference(monkey.friend_of)
    also_friend_of = set(monkey.friend_of).difference(monkey.friends)

    # Populating the lists and sorting them could be done in one step,
    # but I find this a lot more readable:

    sort_order = lambda monkey: (monkey.first_name.lower(), monkey.last_name.lower(), -len(monkey.friends))

    mutual_friends = sorted(mutual_friends, key=sort_order)
    other_friends  = sorted(other_friends,  key=sort_order)
    also_friend_of = sorted(also_friend_of, key=sort_order)

    return {'mutual_friends': mutual_friends,
            'other_friends':  other_friends,
            'also_friend_of': also_friend_of}

def edit_monkey_profile(monkey, form):
    """Edit monkey's profile."""
    # Populate the monkey object with data from the form:
    form.populate_obj(monkey)

    try:
        if monkey.date_of_birth == '':
            # Handling empty birth dates:
            monkey.date_of_birth = None
        else:
            # Handling different date formats:
            monkey.date_of_birth = parser.parse(form['date_of_birth'].data).date()
        db.session.commit()
        return True
    except Exception as e:
        if type(e) is ValueError:
            form.date_of_birth.errors.append('Incorrect date format')
        db.session.rollback()
        return False

def add_friend(monkey, friend):
    """Add a friend to a monkey."""
    if friend is not monkey and friend not in monkey.friends:
        monkey.friends.append(friend)
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

def remove_friend(monkey, friend):
    """Remove a monkey from friends."""
    if friend in monkey.friends:
        monkey.friends.remove(friend)
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False

def set_best_friend(monkey, best_friend):
    """Make one monkey another monkey's best friend."""
    if best_friend and monkey is not best_friend:
        monkey.best_friend = best_friend
        try:
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    else:
        # Non-existent or own id in the URL
        return False

def clear_best_friend(monkey):
    """Clear monkey's best friend."""
    monkey.best_friend_id = None
    try:
        db.session.commit()
        return True
    except Exception:
        db.session.rollback()
        return False

def list_monkeys(order=None, page=1):
    """List all monkeys."""

    # Sorting is done by tuples, so that first name, last name and number of friends are taken into account
    # in all sorting modes (but in different order).
    
    # friend_count==0 evaluates to True when a monkey has no friends specified. This makes sure that
    # the monkeys with friends are listed first (since False < True).

    subquery = db.session.query(friendship.c.left_monkey_id, func.count('*').\
        label('friend_count')).group_by(friendship.c.left_monkey_id).subquery()

    m_alias = aliased(Monkey)

    monkeys_per_page = 10
    
    if order == 'best_friend':
        monkeys = Monkey.query.outerjoin(subquery, Monkey.id==subquery.c.left_monkey_id).\
            outerjoin(m_alias, m_alias.id==Monkey.best_friend_id).\
            order_by(func.lower(m_alias.first_name),
                     func.lower(m_alias.last_name),
                     func.lower(Monkey.first_name),
                     func.lower(Monkey.last_name),
                     subquery.c.friend_count==0,
                     subquery.c.friend_count.desc()).paginate(page, monkeys_per_page)
    elif order == 'friends':
        monkeys = Monkey.query.outerjoin(subquery, Monkey.id==subquery.c.left_monkey_id).\
            order_by(subquery.c.friend_count==0,
                     subquery.c.friend_count.desc(),
                     func.lower(Monkey.first_name),
                     func.lower(Monkey.last_name)).paginate(page, monkeys_per_page)
    else:
        monkeys = Monkey.query.outerjoin(subquery, Monkey.id==subquery.c.left_monkey_id).\
            order_by(func.lower(Monkey.first_name),
                     func.lower(Monkey.last_name),
                     subquery.c.friend_count==0,
                     subquery.c.friend_count.desc()).paginate(page, monkeys_per_page)
    
    return monkeys
