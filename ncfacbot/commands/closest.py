"Closest tick calculator command"

# stdlib
import calendar
from datetime import datetime, timedelta, timezone
import typing
# local
from .. import bot, log
from ..common import FIFTEEN_MINS, THUMBS_DOWN, get_next_tick


@bot.command(brief='Get closest tick to provided time')
async def closest(ctx, hours: typing.Optional[int] = 0,
                  minutes: typing.Optional[int] = 0):
    """
    Get closest tick to provided time

    Displays the GMT time of the closest tick which occurs after the provided offset. You may omit minutes, but hours are required. If you wish to omit hours and only use minutes, use a value of 0. If no values are provided, the next tick is shown.
    """

    if hours < 0 or minutes < 0:
        # nope.
        await ctx.message.add_reaction(THUMBS_DOWN)
        log.warn(f'{ctx.author} made rejected closest request of '
                 f'{hours} hours and {minutes} minutes')
        return

    future_tick = get_next_tick()
    diff = future_tick - datetime.now(timezone.utc) + timedelta(seconds=1)

    if hours > 1 or minutes > (diff.total_seconds() / 60):
        # only bother calculating future tick if it's not the next one
        future_tick += timedelta(hours=hours,
                                 minutes=(minutes - (minutes % 15) + 15))

    tick_str = future_tick.strftime('%a %Y-%m-%d %H:%M:%S %Z')
    await ctx.send(tick_str)
    log.info(f'{ctx.author} requested closest tick (offset {hours}h '
             f'{minutes}m: {tick_str})')
