"Web application entry point"

# stdlib
from os import environ
# local
from . import app

if __name__ == '__main__':
    app.run(host=environ.get('NCFACBOT_HOST', '0.0.0.0'),
            port=int(environ.get('NCFACBOT_PORT', 5000)))
