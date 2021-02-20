"""
Name-only extension; enable per-server or -channel to disable command prefix
and only respond to commands when addressed directly.
"""

# 3rd party
from discord import DMChannel
from discord.ext.commands import Context
# local
from aethersprite import log
from aethersprite.settings import register, settings


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
             'If set, the bot will only respond when directly mentioned. '
             '__**Note**__: It is _extremely_ important that you give the bot '
             'a nickname before setting this. If the bot does not have a nick '
             'set, its username will be the same as its role and it will be '
             'very difficult to mention it directly, potentially bricking the '
             'bot altogether.')
    register('nameonly.channel', None, lambda x: True, True,
             'If set, the bot will only respond when mentioned directly '
             '(in this channel). **See warning from `nameonly` setting.**')
