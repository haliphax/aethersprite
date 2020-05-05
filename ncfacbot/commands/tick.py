"Next game tick command"

# stdlib
import calendar
from datetime import datetime, timezone
from math import floor
from random import randrange
import typing
# local
from .. import log
from ..common import (bot_command, DATETIME_FORMAT, THUMBS_DOWN, get_next_tick,
                      normalize_username, seconds_to_str,)

#: Future/past tick limit
TICK_LIMIT = 1000
#: Silly stuff to say for past ticks
SILLY = (
    ', when the west was still wild...',
    ', when I was a younger bot and still had all my wits about me!',
    '... in the before-time, the long-long-ago.',
    ', if you can believe that!',
    ', okay?',
    '! You remember that?! Man, those were some good times.',
)
SILLY_LEN = len(SILLY)


@bot_command(brief='Next game tick or time [n] ticks from now')
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
    future_tick = get_next_tick(n)
    tick_str = future_tick.strftime(f'{DATETIME_FORMAT} - ')
    # convert to unix timestamps because it's easier to do this with the
    # modulus operator (%) than it is to do this with timespan tomfoolery
    diff = abs(calendar.timegm(future_tick.timetuple())
               - calendar.timegm(datetime.now(timezone.utc).timetuple()))
    until = seconds_to_str(diff)

    if not len(until) and n > 0:
        until = ' right now!'
    elif n >= 0:
        until += ' from now'
    elif n < 0:
        until += ' before now' + SILLY[randrange(SILLY_LEN)]

    tick_str += until
    await ctx.send(f':calendar: {tick_str}')
    log.info(f'{ctx.author} requested next tick: {tick_str}')
