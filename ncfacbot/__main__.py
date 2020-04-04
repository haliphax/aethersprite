# stdlib
from os import environ
from random import seed
# local
from . import bot, log
from .commands import *


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


assert 'DISCORD_TOKEN' in environ, \
    'DISCORD_TOKEN not found in environment variables'
# for any commands or scheduled tasks, etc. that need random numbers
seed()
bot.run(environ['DISCORD_TOKEN'])
