"""
The flask application package.
"""

from os import environ

from flask import Flask
from flask_bootstrap import Bootstrap

from MonkeyBook.models import db

app = Flask(__name__)
Bootstrap(app)

if environ.get('HEROKU'):
    # Running on Heroku
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql://rcfkjeoyxrtceo:QBILLu1p7QLZEcKjqZu26w63hQ@ec2-107-20-166-127.compute-1.amazonaws.com:5432/dflcvf1qdmh8rs'
else:
    # Running locally
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        'postgresql://postgres:postgres@localhost/monkeydb'

db.app = app
db.init_app(app)

import MonkeyBook.views
