"Prefix command"

# 3rd party
from discord.ext.commands import Context
from discord.ext.commands.bot import Bot
from sqlitedict import SqliteDict
# api
from aethersprite import data_folder
from aethersprite.settings import register, settings

prefixes = SqliteDict(f'{data_folder}prefix.sqlite3', tablename='prefixes',
                      autocommit=True)


def get_prefixes(ctx: Context):
    "Get bot prefixes."

    return settings['prefix'].get(ctx)


def setup(bot: Bot):
    register('prefix', None, lambda _: True, False,
             "The bot's command prefix. Note that it will still respond when "
             'mentioned directly.')


def teardown(bot: Bot):
    global settings

    del settings['prefix']
