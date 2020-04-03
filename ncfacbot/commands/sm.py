# stdlib
import asyncio as aio
from datetime import datetime as dt
from time import time
# local
from .. import bot, log
# 3rd party
from discord import DMChannel

timers = {}
FIVE_MINS = 60 * 5
FIFTEEN_MINS = 60 * 15


@bot.command(help='Start a Sorcerers Might timer for <n> minutes')
async def sm(ctx, n: int):
    if ctx.channel is DMChannel:
        await ctx.send('Sorry, but this command must be used in a channel.')
        return

    # normalize nick
    name = str(ctx.author)[:-5]

    if ctx.author.nick is not None:
        name = ctx.author.nick

    if name in timers:
        timers[name].cancel()
        del timers[name]
        await ctx.send('Your existing timer has been removed.')

    now = time()
    sm_end = now + (60 * n)
    next_tick = (now + FIFTEEN_MINS) - (now % FIFTEEN_MINS)
    output = f'```{name} has started a Sorcerers Might timer for {n} minutes.'

    # adjust for SM bug
    if sm_end > next_tick:
        while sm_end > next_tick:
            diff = sm_end - next_tick

            if diff <= FIVE_MINS:
                sm_end -= diff
                break

            next_tick = next_tick + FIFTEEN_MINS
            sm_end -= FIVE_MINS

        reduced = int((sm_end - now) / 60)
        output += f' Adjusting to {reduced} due to SM bug.'
        n = reduced

    output += '```'
    await ctx.send(output)
    loop = aio.get_event_loop()

    def f(name):
        "Countdown completed callback"

        try:
            aio.gather(loop.create_task(ctx.send(
                f'```Sorcerers Might countdown ended for {name}!```')))
        finally:
            del timers[name]

    timers[name] = loop.call_later(60 * n, f, name)
