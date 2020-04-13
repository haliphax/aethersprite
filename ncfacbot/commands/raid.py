"Raid scheduling/announcing command"

# stdlib
import asyncio as aio
from datetime import datetime
from time import mktime
# 3rd party
from discord import DMChannel
from discord.ext import commands
# local
from .. import bot, log


class Raid(commands.Cog):

    "Raid commands cog"

    def __init__(self, bot):
        self.bot = bot
        self._schedule = None
        self._target = None
        self._leader = None

        if self._handle is not None:
            self._handle.cancel()

        self._handle = None

    def _go(self, ctx):
        "Helper method for scheduling announcement callback"

        def announce():
            ctx.send(f':crossed_swords: Time to raid {self._target}!')
            self.__init__(self.bot)

        if self._target is None or self._schedule is None:
            return

        if self._handle is not None:
            self._handle.cancel()

        self._handle = aio.call_at(mktime(self._schedule.timetuple()),
                                   announce)
        ctx.send(f':stopwatch: Raid on {self._target} scheduled for '
                 f'{self._schedule}!')

    @commands.command()
    def cancel(self, ctx):
        "Cancels a currently scheduled raid"

        if type(ctx.channel) is DMChannel:
            ctx.send('This command must be used in a channel.')

            return

        if self._target is None:
            ctx.send(':person_shrugging: There is no scheduled raid.')
            log.info(f'{ctx.author} attempted to cancel nonexistent raid')

            return

        self.__init__(self.bot)
        ctx.send(':negative_squared_cross_mark: Raid canceled.')
        log.info(f'{ctx.author} canceled raid')

    @commands.command()
    def check(self, ctx):
        "Check current raid schedule"

        if self._handle is None:
            ctx.send(f':person_shrugging: There is no scheduled raid.')

            return

        ctx.send(f':mechanical_arm: Raid on {self._target} scheduled for '
                 f'{self._target} by {self._leader}.')

    @commands.command(brief='Schedule a raid')
    def schedule(self, ctx, *, when: datetime):
        "Schedule a raid for [when], which must be a valid datetime string (e.g. 2020-01-01 12:15 AM). Will be considered as GMT."

        self._schedule = when
        ctx.send(f':calendar: Schedule set to {when}.')
        log.info(f'{ctx.author} set raid schedule: {when}')
        self._go()

    @commands.command()
    def target(self, *, target):
        "Set raid target"

        self._target = target
        ctx.send(f':skull_crossbones: Target set to {target}.')
        log.info(f'{ctx.author} set raid target: {target}')
        self._go()

bot.add_cog(Raid(bot))
