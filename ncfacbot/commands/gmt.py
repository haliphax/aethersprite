"GMT time check and offset command"

# stdlib
from datetime import datetime, timedelta, timezone
import typing
# local
from .. import bot, log


@bot.command(brief='Get current time or offset in GMT')
async def gmt(ctx, hours: typing.Optional[int], minutes: typing.Optional[int]):
    """
    Get current time in GMT or offset by [hours] and [minutes]

    To get the current time, no arguments are necessary.

    To get offset time (e.g. 5 hours from now), provide values for hours, minutes, or both. For offsets in the past, use negative numbers.
    """

    offset = datetime.now(timezone.utc)

    if hours is not None:
        offset += timedelta(hours=hours)

    if minutes is not None:
        offset += timedelta(minutes=minutes)

    await ctx.send(offset.strftime('%a %Y-%m-%d %H:%M:%S %Z'))
