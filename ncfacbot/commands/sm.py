"Sorcerers Might countdown command"

# stdlib
import asyncio as aio
from datetime import datetime as dt
from math import ceil
from time import time
import typing
# local
from .. import bot, log
# 3rd party
from discord import DMChannel

# constants

FIVE_MINS = 300
FIFTEEN_MINS = 900
#: Maximum allowed timer length
SM_LIMIT = 120

#: Countdown callback handles
countdowns = {}


@bot.command(brief='Start a Sorcerers Might countdown')
async def sm(ctx, n: typing.Optional[int]):
    """
    Start a Sorcerers Might countdown for n minutes
    
    You may also use a value of 0 to cancel the countdown. If no value is provided, the remaining time of the countdown will be shown.

    * Takes into account the current bug in Sorcerers Might where 5 minutes are deducted erroneously with each game tick.
    """

    if type(ctx.channel) is DMChannel:
        await ctx.send('This command must be used in a channel.')
        return

    loop = aio.get_event_loop()

    # normalize nick

    name = ctx.author.name

    if ctx.author.nick is not None:
        name = ctx.author.nick

    if n is None:
        # report countdown status
        if name not in countdowns:
            await ctx.send('You do not currently have a countdown.')
            return

        remaining = ceil((countdowns[name][0] - time()) / 60)
        minutes = 'minutes' if remaining > 1 else 'minute'

        if remaining < 1:
            await ctx.send('Less than 1 minute remaining!')
        else:
            await ctx.send(f'{remaining} {minutes} to go.')

        log.info(f'{ctx.author} checking SM status: {remaining} {minutes}')
        return
            
    minutes = 'minutes' if n > 1 else 'minute'

    if n > SM_LIMIT:
        # let's not be silly, now
        await ctx.message.add_reaction('\U0001F44E')
        log.info(f'{ctx.author} made rejected SM countdown request of {n} '
                 f'{minutes}')
        return

    if name in countdowns:
        # cancel callback, if any
        countdowns[name][1].cancel()

        try:
            del countdowns[name]
        except KeyError:
            # overlapping requests due to lag can get out of sync
            pass

        await ctx.send('Your countdown has been canceled.')
        log.info(f'{ctx.author} canceled SM countdown')

        # if no valid duration supplied, we're done
        if n < 1:
            return
    elif n < 1:
        await ctx.send('You do not currently have a countdown.')
        log.info(f'{ctx.author} failed to cancel nonexistent SM countdown')
        return

    output = (f'```{name} has started a Sorcerers Might countdown for {n} '
              f'{minutes}.')

    # adjust for SM bug
    now = time()
    sm_end = now + (60 * n)
    next_tick = (now + FIFTEEN_MINS) - (now % FIFTEEN_MINS)

    if sm_end > next_tick:
        dummy_sm = sm_end

        # walk through SM duration and subtract 5 mins for each AP tick
        while True:
            diff = dummy_sm - next_tick

            if diff < FIVE_MINS:
                # less than 5 minute(s) left; shave off the difference and break
                dummy_sm -= diff
                break

            next_tick = next_tick + FIFTEEN_MINS
            dummy_sm -= FIVE_MINS

        reduced = max(1, int((dummy_sm - now) / 60))

        if reduced != n:
            output += f' (Adjusting to {reduced} due to SM bug.)'
            n = reduced
            sm_end = now + (60 * n)

    output += '```'

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
    countdowns[name] = (sm_end, loop.call_later(60 * n, done))
    await ctx.send(output)
    log.info(f'{ctx.author} started SM countdown for {n} {minutes}')
