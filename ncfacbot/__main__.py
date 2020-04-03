# local
from . import bot, DISCORD_TOKEN, log
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

bot.run(DISCORD_TOKEN)
