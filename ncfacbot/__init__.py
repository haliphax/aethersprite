"Nexus Clash Faction Discord bot"

# stdlib
import logging
import sys
# 3rd party
from discord.ext import commands

log = logging.getLogger(__name__)
streamHandler = logging.StreamHandler(sys.stdout)
streamHandler.setFormatter(logging.Formatter(
    '{asctime} {levelname:<7} {message} <{module}.{funcName}>', style='{'))
log.addHandler(streamHandler)
log.setLevel(logging.INFO)
bot = commands.Bot(command_prefix='!')
