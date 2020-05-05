"Sorcerers Might countdown command"

# stdlib
import asyncio as aio
from datetime import datetime, timezone, timedelta
from math import ceil, floor
from time import time
import typing
# 3rd party
from discord.ext import commands
from sqlitedict import SqliteDict
# local
from .. import log
from ..authz import channel_only, require_roles
from ..common import (command, FIFTEEN_MINS, get_next_tick, FakeContext,
                      normalize_username, startup, THUMBS_DOWN,)
from ..settings import register, settings

#: Maximum allowed timer length
SM_LIMIT = 55
#: Countdown callback handles
countdowns = {}
#: Countdown schedule persisted to database file
schedule = SqliteDict('sm.sqlite3', tablename='announce', autocommit=True)

#: Bot reference for startup
_bot = None


class SMSchedule(object):

    "Sorcerer's Might expiry announcement schedule"

    def __init__(self, user, nick, channel, schedule):
        #: The full user name
        self.user = user
        #: The user's nick/name
        self.nick = nick
        #: The channel where the request was made
        self.channel = channel
        #: The time to announce
        self.schedule = schedule


def _done(guild, channel, user, nick):
    "Countdown completed callback"

    global countdowns

    loop = aio.get_event_loop()
    FakeContext = namedtuple('FakeContext', ('guild',))
    int_guild = int(guild)
    fake_ctx = None

    try:
        fake_ctx = FakeContext(guild=[g for g in _bot.guilds
                                      if g.id == int_guild][0])
    except IndexError:
        # guild isn't registered with this bot; remove it
        log.warn(f'Removing missing guild {guild}')
        del schedule[guild]
        del countdowns[user]

        return

    try:
        role = settings['sm.medicrole'].get(fake_ctx)
        chan = settings['sm.channel'].get(fake_ctx)

        msg = f':adhesive_bandage: Sorcerers Might ended for {nick}!'

        # determine the announcement channel
        if chan is None:
            chan = channel

        # get the medic role, if any
        try:
            medic = [r for r in fake_ctx.guild.roles if r.name == role][0]
            msg = f'{medic.mention} ' + msg
        except IndexError:
            pass

        chan = chan.lower().strip()

        try:
            where = [c for c in fake_ctx.guild.channels
                     if c.name.lower() == chan][0]
            # ctx.send is a coroutine, but we're in a plain function, so we
            # have to wrap the call to ctx.send in a Task
            loop.create_task(where.send(msg))
            log.info(f'{user} completed SM countdown')
        except IndexError:
            log.error(f'Unable to announce SM countdown for {nick} in {chan}')

            return
    finally:
        if guild in countdowns:
            if user in countdowns[guild]:
                g = countdowns[guild]
                del g[user]
                countdowns[guild] = g

            if user in schedule[guild]:
                s = schedule[guild]
                del s[user]
                schedule[guild] = s


@startup
async def on_ready():
    "Schedule countdowns from database; immediately announce those missed"

    global countdowns

    if len(countdowns):
        # only have to do this once during initial connect
        return

    now = datetime.now(timezone.utc)
    loop = aio.get_event_loop()

    for gid, guild in schedule.items():
        for _, sched in guild.items():
            if sched.schedule <= now:
                log.info(f'Immediately calling SM expiry for {sched.user}')
                _done(gid, sched.channel, sched.user, sched.nick)
            else:
                log.info(f'Scheduling SM expiry for {sched.user}')
                diff = (sched.schedule - now).total_seconds()
                h = loop.call_later(diff, _done, gid, sched.channel,
                                    sched.user, sched.nick)

                if gid not in countdowns:
                    countdowns[gid] = {}

                cd = countdowns[gid]
                cd[sched.user] = (sched.schedule, h)
                countdowns[gid] = cd


@command(brief='Start a Sorcerers Might countdown', name='sm')
@commands.check(channel_only)
async def sm(ctx, n: typing.Optional[int]=None):
    """
    Start a Sorcerers Might countdown for n minutes

    You may also use a value of 0 to cancel the countdown. If no value is provided, the remaining time of the countdown will be shown.

    Values of n up to 55 are allowed.

    * Takes into account the current bug in Sorcerers Might where 5 minutes are deducted erroneously with each game tick.
    """

    global countdowns

    author = str(ctx.author)
    guild = str(ctx.guild.id)
    loop = aio.get_event_loop()
    nick = normalize_username(ctx.author)
    now = datetime.now(timezone.utc)

    if n is None:
        # report countdown status
        if guild not in countdowns \
                or author not in countdowns[guild]:
            await ctx.send(':person_shrugging: '
                           'You do not currently have a countdown.')

            return

        cd = countdowns[guild][author]

        # get remaining time
        remaining = (cd[0] - now).total_seconds() / 60

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

    # cancel callback, if any
    if guild in countdowns and author in countdowns[guild]:
        countdowns[guild][author][1].cancel()

    if guild in countdowns:
        if author in countdowns[guild]:
            g = countdowns[guild]
            del g[author]
            countdowns[guild] = g

        if author in schedule[guild]:
            s = schedule[guild]
            del s[author]
            schedule[guild] = s

            await ctx.send(':negative_squared_cross_mark: '
                           'Your countdown has been canceled.')
            log.info(f'{ctx.author} canceled SM countdown')

            # if no valid duration supplied, we're done
            if n < 1:
                return

    if n < 1:
        await ctx.send(':person_shrugging: '
                       'You do not currently have a countdown.')
        log.warn(f'{ctx.author} failed to cancel nonexistent SM countdown')

        return

    output = (f':alarm_clock: Starting a Sorcerers Might countdown for {n} '
              f'{minutes}.')
    sm_end = now + timedelta(minutes=n) \
        - timedelta(seconds=now.second, microseconds=now.microsecond)
    counter = 1
    next_tick = get_next_tick()

    while next_tick < sm_end:
        counter += 1
        diff = floor((sm_end - next_tick).total_seconds() / 60)

        if diff > 5:
            sm_end -= timedelta(minutes=5)
        else:
            sm_end = next_tick

            break

        next_tick = get_next_tick(counter)

    new_count = ceil((sm_end - now).total_seconds() / 60)

    if new_count != n:
        output += f' (Adjusting to {new_count} due to SM bug.)'

    # store countdown reference in database
    if not guild in schedule:
        # first time; make a space for this server
        schedule[guild] = {}

    sched = schedule[guild]
    sched[author] = SMSchedule(author, nick, ctx.channel.name,
                               sm_end + timedelta(minutes=1))
    schedule[guild] = sched

    # set timer for countdown completed callback
    if not guild in countdowns:
        countdowns[guild] = {}

    cd = countdowns[guild]
    cd[author] = (sm_end, loop.call_later(60 * (new_count + 1), _done,
                                          guild, ctx.channel.name, author, nick))
    countdowns[guild] = cd
    await ctx.send(output)
    log.info(f'{ctx.author} started SM countdown for {n} ({new_count}) '
             f'{minutes}')


def setup(bot):
    global _bot

    # settings
    register('sm.medicrole', 'medic', lambda x: True, False,
             'The Discord server role used for announcing SM countdown '
             'expirations. Will be suppressed if it doesn\'t exist.')
    register('sm.channel', None, lambda x: True, False,
             'The channel where SM countdown expiry announcements will be '
             'posted. If set to the default, they will be announced in the '
             'same channel where they were last manipulated (per-user).')
    _bot = bot
    bot.add_command(sm)


def teardown(bot):
    global settings

    for k in ('sm.medicrole', 'sm.channel'):
        del settings[k]
