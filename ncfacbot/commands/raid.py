"Raid scheduling/announcing command"

# stdlib
import asyncio as aio
from datetime import datetime, timezone
from math import ceil
# 3rd party
from discord.ext import commands
# local
from .. import bot, log
from ..common import (channel_only, DATETIME_FORMAT, normalize_username,
                      THUMBS_DOWN, seconds_to_str,)

INPUT_FORMAT = '%Y-%m-%d %H:%M %z'
MSG_NO_RAID = ':person_shrugging: There is no scheduled raid.'


class Raid(commands.Cog, name='raid'):

    """
    Raid commands

    NOTE: A raid will not actually be scheduled until both a schedule AND a target have been set. Until then, check and cancel commands will get a "There is no scheduled raid" message.
    """

    _handle = None

    def __init__(self, bot):
        self.bot = bot
        self._schedule = None
        self._target = None
        self._leader = None

        if self._handle is not None:
            self._handle.cancel()

        self._handle = None

    async def _go(self, ctx):
        "Helper method for scheduling announcement callback"

        loop = aio.get_event_loop()

        def reminder1():
            loop.create_task(
                ctx.send(f':stopwatch: @here '
                         f'Raid on {self._target} in 30 minutes!'))
            log.info(f'30 minute reminder for {self._target} @ '
                     f'{self._schedule}')
            self._handle = loop.call_later(900, reminder2)

        def reminder2():
            loop.create_task(
                ctx.send(f':stopwatch: @here '
                         f'Raid on {self._target} in 15 minutes!'))
            log.info(f'15 minute reminder for {self._target} @ '
                     f'{self._schedule}')
            self._handle = loop.call_later(900, announce)

        def announce():
            loop.create_task(
                ctx.send(f':crossed_swords: @everyone '
                         f'Time to raid {self._target}!'))
            log.info(f'Announcement for {self._target}')
            self.__init__(self.bot)

        self._leader = normalize_username(ctx.author)

        if self._target is None or self._schedule is None:
            return

        if self._handle is not None:
            self._handle.cancel()

        wait = (self._schedule - datetime.now(timezone.utc)).total_seconds()

        if wait <= 0:
            await ctx.send(':negative_squared_cross_mark: Raid is in the '
                           'past; canceling it.')
            log.warning(f'Automatically canceling past raid {self._schedule}')
            self.__init__(self.bot)

            return

        if wait > 1800:
            self._handle = loop.call_later(wait - 1800, reminder1)
            log.info(f'Set 30 minute reminder for {self._target}')
        elif wait > 900:
            self._handle = loop.call_later(wait - 900, reminder2)
            log.info(f'Set 15 minute reminder for {self._target}')
        else:
            log.info(f'Scheduled announcement for {self._target}')
            self._handle = loop.call_later(wait, announce)

        await ctx.send(f':white_check_mark: Raid on {self._target} scheduled '
                       f'for {self._schedule.strftime(DATETIME_FORMAT)}!')
        log.info(f'{ctx.author} scheduled raid on {self._target} @ '
                 f'{self._schedule}')

    @commands.command(name='raid.cancel')
    @channel_only
    async def cancel(self, ctx):
        "Cancels a currently scheduled raid"

        if self._target is None:
            await ctx.send(MSG_NO_RAID)
            log.info(f'{ctx.author} attempted to cancel nonexistent raid')

            return

        self.__init__(self.bot)
        await ctx.send(':negative_squared_cross_mark: Raid canceled.')
        log.info(f'{ctx.author} canceled raid')

    @commands.command(name='raid.check')
    @channel_only
    async def check(self, ctx):
        "Check current raid schedule"

        if self._handle is None:
            await ctx.send(MSG_NO_RAID)

            return

        until = seconds_to_str(
            (self._schedule - datetime.now(timezone.utc)).total_seconds())
        await ctx.send(f':pirate_flag: Raid on {self._target} scheduled '
                       f'for {self._schedule.strftime(DATETIME_FORMAT)} by '
                       f'{self._leader}. ({until} from now)')

    @commands.command(name='raid.schedule', brief='Set raid schedule')
    @channel_only
    async def schedule(self, ctx, *, when):
        """
        Set raid schedule to [when], which must be a valid 24-hour datetime string (e.g. 2020-01-01 23:45). Date is optional; today's date will be the default value. Will be parsed as GMT.

        Examples:

            !raid.schedule 2020-01-01 23:45
            !raid.schedule 23:45
        """

        dt = datetime.now(timezone.utc)

        try:
            if '-' in when:
                dt = datetime.strptime(when + ' +0000', INPUT_FORMAT)
            else:
                dt = datetime.strptime(f'{dt.strftime("%Y-%m-%d")} {when} '
                                       '+0000',
                                       INPUT_FORMAT)

            self._schedule = dt
            await ctx.send(f':calendar: Schedule set to '
                           f'{dt.strftime(DATETIME_FORMAT)}.')
            log.info(f'{ctx.author} set raid schedule: {dt}')
            await self._go(ctx)
        except:
            await ctx.message.add_reaction(THUMBS_DOWN)
            log.warning(f'{ctx.author} provided bad args: {when}')

    @commands.command(name='raid.target')
    @channel_only
    async def target(self, ctx, *, target):
        "Set raid target"

        self._target = target
        await ctx.send(f':point_right: Target set to {target}.')
        log.info(f'{ctx.author} set raid target: {target}')
        await self._go(ctx)

bot.add_cog(Raid(bot))
