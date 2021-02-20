"Web application"

# stdlib
from importlib import import_module
from inspect import ismodule
# 3rd party
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
# local
from .. import config, log

#: Flask application
app = Flask(__name__)
app.config.update(config['webapp']['flask'])

proxies = config.get('webapp', {}).get('proxies', None)

if proxies is not None:
    app.wsgi_app = ProxyFix(app.wsgi_app, proxies)

def _load_ext(ext, package=None):
    mod = import_module(ext, package)

    if hasattr(mod, 'META_EXTENSION') and mod.META_EXTENSION:
        for child in mod._mods:
            _load_ext(f'..{child}', ext)

    if not hasattr(mod, 'setup_webapp'):
        return

    log.info(f'Web app setup: {mod.__name__}')
    mod.setup_webapp(app)

# probe extensions for web app hooks
for ext in config['bot']['extensions']:
    _load_ext(ext)
