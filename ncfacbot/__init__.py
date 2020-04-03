"Nexus Clash Faction Discord bot"

# stdlib
import logging
import os
import sys
# 3rd party
from discord.ext import commands

assert 'DISCORD_TOKEN' in os.environ, \
        'DISCORD_TOKEN not found in environment variables'
DISCORD_TOKEN = os.environ['DISCORD_TOKEN']
log = logging.getLogger(__name__)
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(logging.Formatter(
    '{asctime} {levelname} {module}.{funcName}: {message}', style='{'))
log.addHandler(streamHandler)
log.setLevel(logging.INFO)
bot = commands.Bot(command_prefix='!')
