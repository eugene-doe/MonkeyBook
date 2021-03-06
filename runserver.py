"""
This script runs the MonkeyBook application using a development server.
"""

from os import environ

from MonkeyBook import app

if __name__ == '__main__':
    if environ.get('HEROKU'):
        HOST = '0.0.0.0' # Running on Heroku
    else:
        HOST = 'localhost' # Running locally
    try:
        PORT = int(environ.get('PORT', '8080'))
    except ValueError:
        PORT = 8080

    app.run(HOST, PORT) #, debug = True)
