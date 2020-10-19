# stdlib
import logging
from os import environ
from random import seed
from sys import stdout
# 3rd party
from discord import Activity, ActivityType
from discord.ext.commands import (Bot, CheckFailure, CommandNotFound,
                                  when_mentioned_or,)
# local
from . import log

# logging stuff
streamHandler = logging.StreamHandler(stdout)
streamHandler.setFormatter(logging.Formatter(
    '{asctime} {levelname:<7} {message} <{module}.{funcName}>', style='{'))
log.addHandler(streamHandler)
log.setLevel(logging.INFO)

#: Activity on login
activity = Activity(name='!help for commands', type=ActivityType.listening)

#: The bot itself
bot = Bot(command_prefix=when_mentioned_or('!'))


@bot.event
async def on_connect():
    log.info('Connected to Discord')


@bot.event
async def on_disconnect():
    log.info('Disconnected')


@bot.event
async def on_command_error(_, error):
    "Suppress command check failures and invalid commands."

    if isinstance(error, (CheckFailure, CommandNotFound)):
        return

    raise error


@bot.event
async def on_ready():
    "Update presence and fire up registered startup handlers."

    from .common import StartupHandlers

    log.info(f'Logged in as {bot.user}')
    await bot.change_presence(activity=activity)

    for f in StartupHandlers.list:
        await f(bot)


@bot.event
async def on_resumed():
    log.info('Connection resumed')


# redundant, but one last check in case someone wants to get real shifty and
# do something that requires them to import __main__ from another entry point
def entrypoint():
    "ncfacbot main entry point."

    # need credentials
    assert 'DISCORD_TOKEN' in environ, \
        'DISCORD_TOKEN not found in environment variables'
    # for any commands or scheduled tasks, etc. that need random numbers
    seed()
    # load extensions
    bot.load_extension('ncfacbot.extensions._all')
    # here we go!
    bot.run(environ['DISCORD_TOKEN'])

if __name__ == '__main__':
    entrypoint()
