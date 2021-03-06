"Load all command extensions"

META_EXTENSION = True

_mods = (
    'alias',
    'github',
    'greet',
    'gmt',
    'lobotomy',
    'name_only',
    'nick',
    'only',
    'poll',
    'roles',
    'settings',
)
_package = __name__.replace('._all', '')


def setup(bot):
    for m in _mods:
        bot.load_extension(f'{_package}.{m}')


def teardown(bot):
    for m in _mods:
        bot.unload_extension(f'{_package}.{m}')
