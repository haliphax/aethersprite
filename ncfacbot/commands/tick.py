"Next game tick command"

# stdlib
import calendar
from datetime import datetime, timedelta, timezone
from math import floor
import typing
# local
from .. import bot, log
from ..common import THUMBS_DOWN, get_next_tick, normalize_username

# constants
MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
#: Future/past tick limit
TICK_LIMIT = 1000


@bot.command(brief='Next game tick or time [n] ticks from now')
async def tick(ctx, n: typing.Optional[int] = 1):
    """
    Next game tick or time [n] ticks from now in GMT

    Show the next game tick in GMT. Provide a value for <n> to get the GMT timestamp of <n> ticks from now. For past ticks, use a negative number.

    Values of n between -1000 and 1000 are allowed.
    """

    if -TICK_LIMIT > n or n > TICK_LIMIT:
        # let's not be silly, now
        await ctx.message.add_reaction(THUMBS_DOWN)
        log.warn(f'{ctx.author} made rejected next tick request of {n}')
        return

    name = normalize_username(ctx.author)
    future_tick = get_next_tick() + timedelta(minutes=(n - 1) * 15)
    tick_str = future_tick.strftime('%a %Y-%m-%d %H:%M:%S %Z - ')
    diff = abs(calendar.timegm(future_tick.timetuple())
               - calendar.timegm(datetime.now(timezone.utc).timetuple()))
    until = ''

    if diff >= DAY:
        until += f'{floor(diff / DAY)} day(s) '
        diff = diff % DAY

    if diff >= HOUR:
        until += f'{floor(diff / HOUR)} hour(s) '
        diff = diff % HOUR

    if diff >= MINUTE:
        until += f'{floor(diff / MINUTE)} minute(s) '
        diff = diff % MINUTE

    if diff > 0:
        until += f'{diff} second(s) '

    if not len(until) and n > 0:
        until = 'right now!'
    else:
        until += 'from now'

    tick_str += until
    await ctx.send(f':alarm_clock: {tick_str}')
    log.info(f'{ctx.author} requested next tick: {tick_str}')
