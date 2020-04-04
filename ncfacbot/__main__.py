# stdlib
import logging
from os import environ
from random import seed
from sys import stdout
# local
from . import bot, log

# need credentials
assert 'DISCORD_TOKEN' in environ, \
    'DISCORD_TOKEN not found in environment variables'
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
    log.info(f'Logged in as {bot.user} - ready!')


@bot.event
async def on_resumed():
    log.info('Connection resumed')

# load our commands semi-dynamically after everything's set up
from .commands import *
# here we go!
bot.run(environ['DISCORD_TOKEN'])
