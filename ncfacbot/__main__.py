# stdlib
from random import seed
# local
from . import DISCORD_TOKEN, bot, log
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

# for any commands or scheduled tasks, etc. that need random numbers
seed()
bot.run(DISCORD_TOKEN)
