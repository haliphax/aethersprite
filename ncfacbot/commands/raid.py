"Raid scheduling/announcing command"

# stdlib
import asyncio as aio
from datetime import datetime, timezone
from functools import partial
from math import ceil
# 3rd party
from discord.ext import commands
from sqlitedict import SqliteDict
# local
from .. import bot, log
from ..common import (cog_command, channel_only, DATETIME_FORMAT, FakeContext,
                      normalize_username, seconds_to_str, startup, THUMBS_DOWN)
from ..settings import register, require_roles, settings

#: Expected format for schedule input
INPUT_FORMAT = '%Y-%m-%d %H:%M %z'
#: No raid message
MSG_NO_RAID = ':person_shrugging: There is no scheduled raid.'

# settings
register('raid.channel', None, lambda x: True, False,
         'The channel where raids will be announced. If set to the default, '
         'they will be announced in the same channel where the last '
         'modification to the target or schedule was made.')
register('raid.scheduleroles', None, lambda x: True, False,
         'The server roles that are allowed to schedule/cancel raids and set '
         'raid targets. If set to the default, there are no restrictions. '
         'Separate multiple entries with commas.')
register('raid.checkroles', None, lambda x: True, False,
         'The server roles that are allowed to check current raid schedule '
         'and target. If set to the default, there are no restrictions. '
         'Separate multiple entries with commas.')

# authz decorators
authz_schedule = partial(require_roles, setting='raid.scheduleroles')
authz_check = partial(require_roles,
                      setting=('raid.scheduleroles', 'raid.checkroles'))

_schedules = SqliteDict('raid.sqlite3', tablename='schedule',
                        autocommit=True)
_handles = {}


class RaidSchedule(object):

    "Raid schedule; tracks target, time, leader, and channel"

    #: Time of the raid
    schedule = None
    #: The target to raid
    target = None

    def __init__(self, guild, leader, channel):
        #: The guild that owns the raid
        self.guild = int(guild)
        #: Who set the target/schedule
        self.leader = leader
        #: Channel where the last manipulation was done
        self.channel = channel

    def __repr__(self):
        return (f'<RaidSchedule guild={self.guild} target="{self.target}" '
                f'schedule={self.schedule}>')


# helper methods

def _reset(guild):
    "Delete schedule, handle, etc. and reset raid"

    global _handles

    if guild in _handles:
        _handles[guild].cancel()
        del _handles[guild]

    if guild in _schedules:
        del _schedules[guild]


async def _go(raid, ctx, silent=False):
    "Helper method for scheduling announcement callback"

    global _handles

    loop = aio.get_event_loop()
    channel = settings['raid.channel'].get(ctx)

    if channel is None:
        channel = raid.channel

    c = None

    try:
        c = [c for c in ctx.guild.channels if c.name == channel][0]
    except IndexError:
        log.error(f'Unable to find channel {channel} to announce raid')

        return False

    def reminder1():
        loop.create_task(
            c.send(f':stopwatch: @here '
                   f'Raid on {raid.target} in 30 minutes!'))
        log.info(f'30 minute reminder for {raid.target} @ '
                 f'{raid.schedule}')
        _handles[ctx.guild.id] = loop.call_later(900, reminder2)

    def reminder2():
        loop.create_task(
            c.send(f':stopwatch: @here '
                   f'Raid on {raid.target} in 15 minutes!'))
        log.info(f'15 minute reminder for {raid.target} @ '
                 f'{raid.schedule}')
        _handles[ctx.guild.id] = loop.call_later(900, announce)

    def announce():
        loop.create_task(
            c.send(f':crossed_swords: @everyone '
                   f'Time to raid {raid.target}!'))
        log.info(f'Announcement for {raid.target}')
        _reset(ctx.guild.id)

    if raid.target is None or raid.schedule is None:
        return True

    if ctx.guild.id in _handles \
            and _handles[ctx.guild.id] is not None:
        _handles[ctx.guild.id].cancel()
        del _handles[ctx.guild.id]

    wait = (raid.schedule - datetime.now(timezone.utc)).total_seconds()

    if wait <= 0:
        # in the past; announce immediately
        announce()

        return True

    handle = None

    if wait > 1800:
        handle = loop.call_later(wait - 1800, reminder1)
        log.info(f'Set 30 minute reminder for {raid.target}')
    elif wait > 900:
        handle = loop.call_later(wait - 900, reminder2)
        log.info(f'Set 15 minute reminder for {raid.target}')
    else:
        handle = loop.call_later(wait, announce)
        log.info(f'Scheduled announcement for {raid.target}')

    _handles[ctx.guild.id] = handle

    if silent:
        return

    await c.send(f':white_check_mark: Raid on {raid.target} scheduled '
                 f'for {raid.schedule.strftime(DATETIME_FORMAT)}!')
    log.info(f'{raid.leader} scheduled raid on {raid.target} @ '
             f'{raid.schedule}')


@startup
async def on_ready():
    "Schedule raid announcements from database on startup"

    global _handles

    if len(_handles):
        # only have to do this once during initial startup
        return

    for gid, raid in _schedules.items():
        try:
            gid = int(gid)
            ctx = FakeContext([g for g in bot.guilds
                               if g.id == gid][0])
            log.info(raid)
            await _go(raid, ctx, True)
        except IndexError:
            # unknown guild; delete record
            log.error(f'Unknown guild {gid}')
            del _schedules[gid]


class Raid(commands.Cog, name='raid'):

    """
    Raid commands

    NOTE: A raid will not actually be scheduled until both a schedule AND a target have been set. Until then, check and cancel commands will get a "There is no scheduled raid" message.
    """

    def __init__(self, bot):
        self.bot = bot

    @cog_command(name='raid.cancel')
    @authz_schedule
    @channel_only
    async def cancel(self, ctx):
        "Cancels a currently scheduled raid"

        if ctx.guild.id not in _schedules \
                or _schedules[ctx.guild.id].target is None:
            await ctx.send(MSG_NO_RAID)
            log.info(f'{ctx.author} attempted to cancel nonexistent raid')

            return

        _reset(ctx.guild.id)
        await ctx.send(':negative_squared_cross_mark: Raid canceled.')
        log.info(f'{ctx.author} canceled raid')

    @cog_command(name='raid.check')
    @authz_check
    @channel_only
    async def check(self, ctx):
        "Check current raid schedule"

        if ctx.guild.id not in _schedules:
            await ctx.send(MSG_NO_RAID)

            return

        raid = _schedules[ctx.guild.id]
        until = seconds_to_str(
            (raid.schedule - datetime.now(timezone.utc)).total_seconds())
        await ctx.send(f':pirate_flag: Raid on {raid.target} scheduled '
                       f'for {raid.schedule.strftime(DATETIME_FORMAT)} by '
                       f'{raid.leader}. ({until} from now)')

    @cog_command(name='raid.schedule', brief='Set raid schedule')
    @authz_schedule
    @channel_only
    async def schedule(self, ctx, *, when):
        """
        Set raid schedule to <when>, which must be a valid 24-hour datetime string (e.g. 2020-01-01 23:45). Date is optional; today's date will be the default value. Will be parsed as GMT.

        Examples:

            !raid.schedule 2020-01-01 23:45
            !raid.schedule 23:45
        """

        dt = datetime.now(timezone.utc)
        nick = normalize_username(ctx.author)

        try:
            if '-' in when:
                dt = datetime.strptime(when + ' +0000', INPUT_FORMAT)
            else:
                dt = datetime.strptime(f'{dt.strftime("%Y-%m-%d")} {when} '
                                       '+0000',
                                       INPUT_FORMAT)
        except:
            await ctx.message.add_reaction(THUMBS_DOWN)
            log.warning(f'{ctx.author} provided bad args: {when}')

            return

        raid = _schedules[ctx.guild.id] \
                if ctx.guild.id in _schedules \
                else RaidSchedule(ctx.guild.id, nick, ctx.channel.name)
        raid.schedule = dt
        raid.leader = normalize_username(ctx.author)
        _schedules[ctx.guild.id] = raid
        await ctx.send(f':calendar: Schedule set to '
                       f'{dt.strftime(DATETIME_FORMAT)}.')
        log.info(f'{ctx.author} set raid schedule: {dt}')
        await _go(raid, ctx)

    @cog_command(name='raid.target')
    @authz_schedule
    @channel_only
    async def target(self, ctx, *, target):
        "Set raid target"

        nick = normalize_username(ctx.author)
        raid = _schedules[ctx.guild.id] \
                if ctx.guild.id in _schedules \
                else RaidSchedule(ctx.guild.id, nick, ctx.channel.name)
        raid.target = target
        raid.leader = normalize_username(ctx.author)
        _schedules[ctx.guild.id] = raid
        await ctx.send(f':point_right: Target set to {target}.')
        log.info(f'{ctx.author} set raid target: {target}')
        await _go(raid, ctx)

bot.add_cog(Raid(bot))
