"""
Name-only extension; enable per-server or -channel to disable command prefix
and only respond to commands when addressed directly.
"""

# 3rd party
from discord import DMChannel
from discord.ext.commands import Context
# local
from .. import log
from ..settings import register, settings


async def check_name_only(ctx: Context):
    "If the bot wasn't mentioned, refuse the command."

    # don't bother with DMs
    if isinstance(ctx.channel, DMChannel):
        return True

    if (settings['nameonly'].get(ctx) \
                or settings['nameonly.channel'].get(ctx)) \
            and not ctx.bot.user.mentioned_in(ctx.message):
        log.warn(f'{ctx.author} attempted command without mentioning bot')

        return False

    return True


def setup(bot):
    bot.add_check(check_name_only)
    # settings
    register('nameonly', None, lambda x: True, False,
             'If set, the bot will only respond when directly addressed.')
    register('nameonly.channel', None, lambda x: True, True,
             'If set, the bot will only respond when directly addressed '
             '(in this channel).')
