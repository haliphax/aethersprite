"Sorcerers Might countdown command"

# stdlib
import asyncio as aio
from datetime import datetime as dt
from time import time
# local
from .. import bot, log
# 3rd party
from discord import DMChannel

# constants

FIVE_MINS = 60 * 5
FIFTEEN_MINS = 60 * 15
#: Maximum allowed timer length
SM_LIMIT = 120

#: Countdown callback handles
countdowns = {}


@bot.command(help='Start a Sorcerers Might countdown for <n> minutes, '
                  '0 to cancel')
async def sm(ctx, n: int):
    if type(ctx.channel) is DMChannel:
        await ctx.send('This command must be used in a channel.')
        return

    # normalize nick

    name = ctx.author.name

    if ctx.author.nick is not None:
        name = ctx.author.nick

    if n > SM_LIMIT:
        # let's not be silly, now
        await ctx.message.add_reaction('\U0001F44E')
        log.info(f'{ctx.author} made rejected SM timer request of {n} minutes')
        return

    if name in countdowns:
        # cancel existing callback, if any
        countdowns[name].cancel()
        del countdowns[name]
        await ctx.send('Your existing countdown has been canceled.')
        log.info(f'{ctx.author} canceled SM countdown')

        # if no valid duration supplied, we're done
        if n < 1:
            return

    if n < 1:
        await ctx.send('You do not currently have a countdown.')
        log.info(f'{ctx.author} failed to cancel nonexistent SM countdown')
        return

    output = (f'```{name} has started a Sorcerers Might countdown for {n} '
              'minutes.')

    # adjust for SM bug
    now = time()
    sm_end = now + (60 * n)
    next_tick = (now + FIFTEEN_MINS) - (now % FIFTEEN_MINS)

    if sm_end > next_tick:
        # walk through SM duration and subtract 5 mins for each AP tick
        while True:
            diff = sm_end - next_tick

            if diff < FIVE_MINS:
                # less than 5 minutes left; shave off the difference and break
                sm_end -= diff
                break

            next_tick = next_tick + FIFTEEN_MINS
            sm_end -= FIVE_MINS

        reduced = max(1, int((sm_end - now) / 60))

        if reduced != n:
            output += f' (Adjusting to {reduced} due to SM bug.)'
            n = reduced

    output += '```'
    await ctx.send(output)
    loop = aio.get_event_loop()

    def done():
        "Countdown completed callback"

        try:
            # ctx.send is a coroutine, but we're in a plain function, so we
            # have to wrap the call to ctx.send in a Task
            loop.create_task(ctx.send(
                f'```Sorcerers Might countdown ended for {name}!```'))
            log.info(f'{ctx.author} completed SM countdown')
        finally:
            del countdowns[name]

    # set timer for countdown completed callback
    countdowns[name] = loop.call_later(60 * n, done)
    log.info(f'{ctx.author} started SM countdown for {n} minutes')
