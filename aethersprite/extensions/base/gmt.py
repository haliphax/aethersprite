"GMT time check and offset command"

# stdlib
from datetime import datetime, timedelta, timezone
import typing
# 3rd party
from discord.ext.commands import command
# local
from aethersprite import log
from aethersprite.common import DATETIME_FORMAT, get_timespan_chunks


@command(brief='Get current time or offset in GMT', aliases=['utc',])
async def gmt(ctx, *, offset: typing.Optional[str]):
    """
    Get current time in GMT or offset by days, hours, and minutes.

    To get the current time, no arguments are necessary. To get offset time (e.g. 5 hours from now), provide values for days, hours, or minutes. For offsets in the past, use negative numbers.

    Example: !gmt 3d 6h 17m  <-- would request an offset of 3 days, 6 hours, 17 minutes

    Arguments aren't validated, so anything goes... but please be reasonable. The command will silently fail if you choose an offset the bot can't process.
    """

    delta = get_timespan_chunks(offset) if offset else (0, 0, 0)
    days, hours, minutes = delta
    thetime = (datetime.now(timezone.utc)
               + timedelta(days=days, hours=hours, minutes=minutes))
    offset_str = thetime.strftime(DATETIME_FORMAT)
    await ctx.send(f':clock: {offset_str}')
    log.info(f'{ctx.author} requested GMT offset of {delta}: {offset_str}')


def setup(bot):
    bot.add_command(gmt)
