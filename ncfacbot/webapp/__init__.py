"Web application"

# stdlib
from importlib import import_module
import inspect
from os import environ
# 3rd party
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
# local
from .. import extensions

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, environ.get('PROXIES', 1))
_mods = [m for m in dir(extensions) if m[0] != '_']

for m in _mods:
    mod = import_module(f'..extensions.{m}', __name__)

    if not hasattr(mod, 'setup_webapp'):
        continue

    mod.setup_webapp(app)
