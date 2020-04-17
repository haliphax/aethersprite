"Sorcerers Might countdown command"

# stdlib
import asyncio as aio
from datetime import datetime, timezone, timedelta
from math import ceil
from time import time
import typing
# 3rd party
from discord import DMChannel
# local
from .. import bot, log
from ..common import (FIFTEEN_MINS, THUMBS_DOWN, get_next_tick,
                      normalize_username,)

#: Maximum allowed timer length
SM_LIMIT = 120
#: Countdown callback handles
countdowns = {}


@bot.command(brief='Start a Sorcerers Might countdown')
async def sm(ctx, n: typing.Optional[int]):
    """
    Start a Sorcerers Might countdown for n minutes

    You may also use a value of 0 to cancel the countdown. If no value is provided, the remaining time of the countdown will be shown.

    Values of n up to 120 are allowed.

    * Takes into account the current bug in Sorcerers Might where 5 minutes are deducted erroneously with each game tick.
    """

    if type(ctx.channel) is DMChannel:
        await ctx.send('This command must be used in a channel.')
        return

    loop = aio.get_event_loop()
    name = normalize_username(ctx.author)
    now = datetime.now(timezone.utc)

    if n is None:
        # report countdown status
        if name not in countdowns:
            await ctx.send(':person_shrugging: '
                           'You do not currently have a countdown.')
            return

        # get remaining time
        remaining = (countdowns[name][0] - now).total_seconds() / 60

        if remaining > 1:
            remaining = ceil(remaining)

        remaining = int(remaining)
        minutes = 'minutes' if remaining > 1 else 'minute'

        if remaining < 1:
            await ctx.send(':open_mouth: Less than 1 minute remaining!')
        else:
            await ctx.send(f':stopwatch: About {remaining} {minutes} to go.')

        log.info(f'{ctx.author} checking SM status: '
                 f'{"<1" if remaining < 1 else remaining} {minutes}')
        return

    minutes = 'minutes' if n > 1 else 'minute'

    if n > SM_LIMIT:
        # let's not be silly, now
        await ctx.message.add_reaction(THUMBS_DOWN)
        log.warn(f'{ctx.author} made rejected SM countdown request of {n} '
                 f'{minutes}')
        return

    if name in countdowns:
        # cancel callback, if any
        countdowns[name][1].cancel()

        try:
            del countdowns[name]
        except KeyError:
            # overlapping requests due to lag can get out of sync
            log.error(f'Failed removing countdown for {name}')

        await ctx.send(':negative_squared_cross_mark: '
                       'Your countdown has been canceled.')
        log.info(f'{ctx.author} canceled SM countdown')

        # if no valid duration supplied, we're done
        if n < 1:
            return
    elif n < 1:
        await ctx.send(':person_shrugging: '
                       'You do not currently have a countdown.')
        log.warn(f'{ctx.author} failed to cancel nonexistent SM countdown')
        return

    output = (f':alarm_clock: Starting a Sorcerers Might countdown for {n} '
              f'{minutes}.')
    sm_end = now + timedelta(minutes=n+1) \
            - timedelta(seconds=now.second, microseconds=now.microsecond)
    next_tick = get_next_tick()

    if sm_end > next_tick:
        # 5 minutes subtracted for every tick during SM
        diff = int((sm_end - now).total_seconds() / 60)
        until_next = int((next_tick - now).total_seconds() / 60)
        reduction = ceil(diff / 15) * 5

        # does it end on the next tick, tho?
        if n - until_next - reduction <= 0:
            reduction = n - until_next - 1

        if reduction > 0:
            n -= reduction
            output += f' (Adjusting to {n} due to SM bug.)'
            sm_end = now + timedelta(minutes=n)

    def done():
        "Countdown completed callback"

        try:
            msg = f'Sorcerers Might ended for {name}!'

            # get the medic role, if any
            try:
                medic = [r for r in ctx.guild.roles if r.name == "medic"][0]
                msg = f'{medic.mention} ' + msg
            except IndexError:
                pass

            msg = ':adhesive_bandage: ' + msg
            # ctx.send is a coroutine, but we're in a plain function, so we
            # have to wrap the call to ctx.send in a Task
            loop.create_task(ctx.send(msg))
            log.info(f'{ctx.author} completed SM countdown')
        finally:
            del countdowns[name]

    # set timer for countdown completed callback
    countdowns[name] = (sm_end, loop.call_later(60 * (n + 1), done))
    await ctx.send(output)
    log.info(f'{ctx.author} started SM countdown for {n} {minutes}')
