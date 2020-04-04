"Closest tick calculator command"

# stdlib
import calendar
from datetime import datetime, timedelta, timezone
import typing
# local
from .. import bot, log
from ..common import (FIFTEEN_MINS, THUMBS_DOWN, get_datetime_chunks,
                      get_next_tick,)


@bot.command(brief='Get closest tick to time offset')
async def closest(ctx, *, offset: typing.Optional[str]):
    """
    Get closest tick to time offset

    Displays the GMT time of the closest tick which occurs after the provided offset. If no values are provided, the next tick is shown.

    Example: !closest 2h 15m  <-- shows the closest tick 2 hours and 15 minutes from now
    """

    delta = get_datetime_chunks(offset) if offset else (0, 0, 0)

    for val in delta:
        if val < 0:
            # negative numbers are a no-no
            await ctx.message.add_reaction(THUMBS_DOWN)
            log.warn(f'{ctx.author} made rejected closest request of {delta}')
            return

    days, hours, minutes = delta
    future_tick = get_next_tick()
    diff = future_tick - datetime.now(timezone.utc) + timedelta(seconds=1)

    if days > 1 or hours > 1 or minutes > (diff.total_seconds() / 60):
        # only bother calculating future tick if it's not the next one
        future_tick += timedelta(hours=hours,
                                 minutes=(minutes - (minutes % 15) + 15))

    tick_str = future_tick.strftime('%a %Y-%m-%d %H:%M:%S %Z')
    await ctx.send(f':dart: {tick_str}')
    log.info(f'{ctx.author} requested closest tick {delta}: {tick_str}')
