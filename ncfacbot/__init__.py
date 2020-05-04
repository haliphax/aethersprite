"Nexus Clash Faction Discord bot"

# stdlib
import logging
# 3rd party
from discord.ext.commands import Bot

#: Root logger instance
log = logging.getLogger(__name__)
#: The bot itself
bot = Bot(command_prefix='!')
