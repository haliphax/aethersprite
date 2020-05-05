"Load all command extensions"

from .. import extensions

_mods = [m for m in dir(extensions) if m[0] != '_']
_package = __name__.replace('._all', '')


def setup(bot):
    for m in _mods:
        bot.load_extension(f'{_package}.{m}')


def teardown(bot):
    for m in _mods:
        bot.unload_extension(f'{_package}.{m}')
