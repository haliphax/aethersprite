"""Yeet cog"""

# stdlib
import typing

# 3rd party
from discord import DMChannel, TextChannel
from discord.ext.commands import Bot, Cog, command, Context
from discord_argparse import ArgumentConverter, OptionalArgument
from sqlitedict import SqliteDict

# local
from aethersprite import data_folder, log
from aethersprite.authz import require_admin

#: Yeets database
yeets = SqliteDict(f"{data_folder}yeet.sqlite3", tablename="yeets", autocommit=True)


class Yeet(Cog, name="yeet-commands"):
    """Yeet commands; enable and disable commands per-server and per-channel"""

    def __init__(self, bot):
        self.bot = bot

    @command(name="yeet")
    async def add(
        self,
        ctx: Context,
        command: str,
        channel: typing.Optional[TextChannel] = None,
    ):
        """
        Disable the given command

        Disables <command> on this server. Specify a channel to disable only in that channel.

        Examples:
            !yeet test  <-- disables yeet command for entire server
            !yeet test #lobby  <-- disables test command in #lobby channel
        """

        server = True if not channel else False
        channel = ctx.channel if not channel else channel
        server_key = command.lower().strip()
        key = f"{server_key}#{channel.id}"
        guild = str(ctx.guild.id)

        if not ctx.guild.id in yeets:
            yeets[guild] = set([])

        ys = yeets[guild]

        if (key in ys and not server) or (server_key in ys and server):
            await ctx.send(f":newspaper: Already done.")

            return

        # if it's already in the opposite category (channel vs. server),
        # then clear it out
        if key in ys and server:
            ys.remove(key)
        elif server_key in ys and not server:
            ys.remove(server_key)

        ys.add(server_key if server else key)
        yeets[guild] = ys
        log.info(
            f"{ctx.author} yeeted {server_key if server else key} in {ctx.channel}"
        )
        await ctx.send(f":boom: Yeet!")

    @command(name="unyeet")
    async def remove(
        self,
        ctx: Context,
        command: str,
        channel: typing.Optional[TextChannel] = None,
    ):
        """
        Enable the given command

        Enables <command> on this server. Specify a channel to enable only in that channel.

        Examples:
            !unyeet test  <-- enable test command for entire server
            !unyeet test #lobby  <-- enable test command in #lobby channel
        """

        server = True if not channel else False
        channel = ctx.channel if not channel else channel
        server_key = command.lower().strip()
        key = f"{server_key}#{channel.id}"
        guild = str(ctx.guild.id)
        ys = yeets[guild] if guild in yeets else None

        if ys is None:
            await ctx.send(":person_shrugging: None set.")

            return

        if (key in ys and server) or (server_key in ys and not server):
            await ctx.send(":thumbsdown: The opposite scope is active.")

            return

        ys.remove(server_key if server else key)
        yeets[guild] = ys
        log.info(f"{ctx.author} removed {server_key if server else key} in {channel}")
        await ctx.send(":tada: Re-enabled.")

    @command(name="yeets")
    async def list(
        self,
        ctx: Context,
        channel: typing.Optional[TextChannel] = None,
    ):
        """
        List all yeeted commands on this server

        Specify a channel to view only that channel's yeeted commands.

        Examples:
            !yeets  <-- list all yeets on server
            !yeets #lobby  <-- list yeets in #lobby channel
        """

        server = True if not channel else False
        channel = ctx.channel if not channel else channel
        guild = str(ctx.guild.id)

        if guild not in yeets:
            yeets[guild] = []

        suffix = f"#{channel.id}"
        suffixlen = len(suffix)
        output = "**, **".join(
            [
                (l if server else l[:-suffixlen])
                for l in yeets[guild]
                if server or l.endswith(suffix)
            ]
        )

        if not len(output):
            output = "None"

        log.info(
            f'{ctx.author} viewed {"server " if server else""}yeet '
            f"list in {channel}"
        )
        await ctx.send(f":v: **{output}**")


async def check_yeet(ctx: Context):
    """Check that command has not been yeeted before allowing execution."""

    if isinstance(ctx.channel, DMChannel):
        # can't yeet commands via DM, since we need a guild to check
        # settings values
        return True

    guild = str(ctx.guild.id)

    if guild not in yeets:
        # none set for this guild; bail
        return True

    keys = (ctx.command.name, f"{ctx.command.name}#{ctx.channel.id}")

    for k in keys:
        if k in yeets[guild]:
            log.debug(
                f"Suppressing yeeted command from "
                f"{ctx.author}: {ctx.command.name} in "
                f"#{ctx.channel.name} ({ctx.guild.name})"
            )

            return False

    return True


async def setup(bot: Bot):
    bot.add_check(check_yeet)
    cog = Yeet(bot)

    for c in cog.get_commands():
        c.add_check(require_admin)

    await bot.add_cog(cog)
