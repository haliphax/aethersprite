# stdlib
import logging
from os import environ
from random import seed
from sys import stdout
# local
from . import bot, log

# logging stuff
streamHandler = logging.StreamHandler(stdout)
streamHandler.setFormatter(logging.Formatter(
    '{asctime} {levelname:<7} {message} <{module}.{funcName}>', style='{'))
log.addHandler(streamHandler)
log.setLevel(logging.INFO)
# for any commands or scheduled tasks, etc. that need random numbers
seed()


@bot.event
async def on_connect():
    log.info('Connected to Discord')


@bot.event
async def on_disconnect():
    log.info('Disconnected')


@bot.event
async def on_ready():
    from .common import startup_handlers

    log.info(f'Logged in as {bot.user}')

    for f in startup_handlers:
        await f()


@bot.event
async def on_resumed():
    log.info('Connection resumed')

# load our commands semi-dynamically after everything's set up
from .commands import *


# redundant, but one last check in case someone wants to get real shifty and
# do something that requires them to import __main__ from another entry point
def entrypoint():
    # need credentials
    assert 'DISCORD_TOKEN' in environ, \
        'DISCORD_TOKEN not found in environment variables'
    # here we go!
    bot.run(environ['DISCORD_TOKEN'])

if __name__ == '__main__':
    entrypoint()
