"Lobotomy cog"

# stdlib
from os import environ
import typing
# 3rd party
from discord.ext import commands
from functools import partial
# local
from .. import bot, log
from ..common import cog_command
from ..lobotomy import lobotomies
from ..settings import require_admin


class Lobotomy(commands.Cog, name='lobotomy'):

    "Lobotomy commands; enable and disable commands per-server and per-channel"

    def __init__(self, bot):
        self.bot = bot

    @cog_command(name='lobotomy.add')
    @commands.check(require_admin)
    async def add(self, ctx, command, server: typing.Optional[bool] = False):
        """
        Disable the given command

        Disables <command> in this channel. If [server] is True, then the command is disabled on the entire server.
        """

        server_key = command.lower().strip()
        key = f'{server_key}#{ctx.channel.id}'
        guild = str(ctx.guild.id)

        if not ctx.guild.id in lobotomies:
            lobotomies[guild] = set([])

        lobs = lobotomies[guild]

        if (key in lobs and not server) \
                or (server_key in lobs and server):
            await ctx.send(f':newspaper: Already done.')

            return

        if key in lobs and server:
            lobs.remove(key)
        elif server_key in lobs and not server:
            lobs.remove(server_key)

        lobs.add(server_key if server else key)
        lobotomies[guild] = lobs
        await ctx.send(f':brain: Done.')

    @cog_command(name='lobotomy.clear')
    @commands.check(require_admin)
    async def clear(self, ctx, command, server: typing.Optional[bool] = False):
        """
        Enable the given command

        Enables <command> in this channel. If [server] is True, then the command is enabled on the entire server.
        """

        server_key = command.lower().strip()
        key = f'{server_key}#{ctx.channel.id}'
        guild = str(ctx.guild.id)
        lobs = lobotomies[guild] if guild in lobotomies else None

        if lobs is None:
            await ctx.send(':person_shrugging: None set.')

            return

        if (key in lobs and server) or (server_key in lobs and not server):
            await ctx.send(':thumbsdown: The opposite scope is '
                           'currently set.')

            return

        lobs.remove(server_key if server else key)
        lobotomies[guild] = lobs
        await ctx.send(':wastebasket: Cleared.')

    @cog_command(name='lobotomy.list')
    @commands.check(require_admin)
    async def list(self, ctx, server: typing.Optional[bool] = False):
        """
        List all current channel's lobotomized commands

        If [server] is True, all lobotomies for all channels and the server will be shown, instead.
        """

        guild = str(ctx.guild.id)
        suffix = f'#{ctx.channel.id}'
        suffixlen = len(suffix)
        output = '**, **'.join([(l if server else l[:-suffixlen])
                                for l in lobotomies[guild]
                                if server or l.endswith(suffix)])

        if not len(output):
            output = 'None'

        await ctx.send(f':medical_symbol: **{output}**')


bot.add_cog(Lobotomy(bot))
