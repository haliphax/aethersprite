"Nexus Clash Faction Discord bot"

# stdlib
import logging
# 3rd party
from discord.ext.commands import Bot, when_mentioned_or

#: Root logger instance
log = logging.getLogger(__name__)
#: The bot itself
bot = Bot(command_prefix=when_mentioned_or('!'))
