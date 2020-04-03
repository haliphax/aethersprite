# local
from . import bot, DISCORD_TOKEN, log
from .commands import *

@bot.event
async def on_ready():
    log.info(f'Logged in as {bot.user}')


bot.run(DISCORD_TOKEN)
