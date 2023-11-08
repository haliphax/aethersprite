"""Load all extensions"""

# 3rd party
from discord.ext.commands import Bot

META_EXTENSION = True

_mods = (
    "alias",
    "badnames",
    "github",
    "greet",
    "gmt",
    "name_only",
    "nick",
    "only",
    "poll",
    "prefix",
    "roles",
    "settings",
    "wipe",
    "yeet",
)
_package = __name__.replace("._all", "")


async def setup(bot: Bot):
    for m in _mods:
        await bot.load_extension(f"{_package}.{m}")


async def teardown(bot: Bot):
    for m in _mods:
        await bot.unload_extension(f"{_package}.{m}")
