"GMT time check and offset command"

# stdlib
from datetime import datetime, timedelta, timezone
import typing
# local
from .. import bot, log


@bot.command(brief='Get current time or offset in GMT')
async def gmt(ctx, days: typing.Optional[int], hours: typing.Optional[int],
              minutes: typing.Optional[int]):
    """
    Get current time in GMT or offset by [days], [hours] and [minutes]

    To get the current time, no arguments are necessary.

    To get offset time (e.g. 5 hours from now), provide values for days, hours, or minutes. Each argument requires the argument before it (e.g. to provide hours, you must provide days), but providing a value of 0 will ignore the argument. For offsets in the past, use negative numbers.

    Arguments aren't validated, so anything goes... but please be reasonable. The command will silently fail if you choose an offset the bot can't process.
    """

    offset = datetime.now(timezone.utc)

    if days is not None:
        offset += timedelta(days=days)

    if hours is not None:
        offset += timedelta(hours=hours)

    if minutes is not None:
        offset += timedelta(minutes=minutes)

    await ctx.send(offset.strftime('%a %Y-%m-%d %H:%M:%S %Z'))
