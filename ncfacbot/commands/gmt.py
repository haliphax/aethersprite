"GMT time check and offset command"

# stdlib
from datetime import datetime, timedelta, timezone
import typing
# local
from .. import bot, log


@bot.command(brief='Get current time or offset in GMT')
async def gmt(ctx, days: typing.Optional[int] = 0,
              hours: typing.Optional[int] = 0,
              minutes: typing.Optional[int] = 0):
    """
    Get current time in GMT or offset by [days], [hours] and [minutes]

    To get the current time, no arguments are necessary.

    To get offset time (e.g. 5 hours from now), provide values for days, hours, or minutes. Each argument requires the argument before it (e.g. to provide hours, you must provide days), but providing a value of 0 will ignore the argument. For offsets in the past, use negative numbers.

    Arguments aren't validated, so anything goes... but please be reasonable. The command will silently fail if you choose an offset the bot can't process.
    """

    offset = (datetime.now(timezone.utc)
              + timedelta(days=days, hours=hours, minutes=minutes))
    offset_str = offset.strftime('%a %Y-%m-%d %H:%M:%S %Z')
    await ctx.send(offset_str)
    log.info(f'{ctx.author} requested GMT offset of {days}d {hours}h '
             f'{minutes}m: {offset_str}')
