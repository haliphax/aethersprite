"Web application entry point"

# local
from . import app

if __name__ == '__main__':
    app.run(app.config['SERVER_HOST'], app.config['SERVER_PORT'])
