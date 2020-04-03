"Next game tick command"

# stdlib
import calendar
from datetime import datetime, timedelta, timezone
from math import floor
import typing
# local
from .. import bot, log
from ..common import get_next_tick, normalize_username

# constants
MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
#: Future/past tick limit
TICK_LIMIT = 1000


@bot.command(brief='Next game tick')
async def tick(ctx, n: typing.Optional[int] = 1):
    """
    Next game tick

    Show the next game tick in GMT. Provide a value for <n> to get the GMT timestamp of <n> ticks from now. For past ticks, use a negative number.
    """

    if -TICK_LIMIT > n or n > TICK_LIMIT:
        # let's not be silly, now
        await ctx.message.add_reaction('\U0001F44E')
        log.info(f'{ctx.author} made rejected next tick request of {n}')
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
    log.info(f'{ctx.author} requested next tick: {tick_str}')
    await ctx.send(tick_str)
