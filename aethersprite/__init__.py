"Nexus Clash Faction Discord bot"

# stdlib
from importlib import import_module
import logging
from os import environ
# 3rd party
import toml

#: Root logger instance
log = logging.getLogger(__name__)
#: Configuration
config = {
    'bot': {
        'extensions': ['aethersprite.extensions.base._all'],
    },
    'webapp': {
        'proxies': None,
        'flask': {
            'SERVER_NAME': 'localhost',
            'SERVER_HOST': '0.0.0.0',
            'SERVER_PORT': 5000,
        },
    },
}

# Load config from file and merge with defaults
config_file = environ.get('NCFACBOT_CONFIG', './config.toml')
config = {**config, **toml.load(config_file)}

# load webapp just so the config gets set for url_for, etc.
import_module('.webapp', __name__)
