"""Only cog"""

# TODO server whitelist

# 3rd party
from discord import DMChannel
from discord.channel import TextChannel
from discord.ext.commands import Cog, command, Context
from sqlitedict import SqliteDict

# local
from aethersprite import data_folder, log
from aethersprite.authz import channel_only, require_admin

onlies = SqliteDict(
    f"{data_folder}only.sqlite3", tablename="onlies", autocommit=True
)
"""Only whitelist database"""


class Only(Cog):
    """Only commands; disable all commands except for those in a whitelist"""

    def __init__(self, bot):
        self.bot = bot

    @command(name="only.add")
    async def add(
        self,
        ctx: Context,
        command: str,
        channel: TextChannel | None = None,
    ):
        """
        Add the given command to the Only whitelist

        Enables <command> in this channel.

        You may specify a channel other than the current one.

        Examples:
            !only.add test
            !only.add test #lobby
        """

        assert ctx.guild

        if not channel:
            channel = ctx.channel  # type: ignore
            assert channel

        chan_id = str(channel.id)
        guild = str(ctx.guild.id)

        if guild not in onlies:
            onlies[guild] = dict()

        ours = onlies[guild]

        if chan_id not in ours:
            ours[chan_id] = set([])

        ourchan = ours[chan_id]

        if command in ourchan:
            await ctx.send(":newspaper: Already done.")

            return

        ourchan.add(command)
        ours[chan_id] = ourchan
        onlies[guild] = ours
        log.info(f"{ctx.author} added {command} to {channel} whitelist")
        await ctx.send(":shield: Done.")

    @command(name="only.remove")
    async def remove(
        self,
        ctx: Context,
        command: str,
        channel: TextChannel | None = None,
    ):
        """
        Remove the given command from the Only whitelist

        If whitelisting is enabled for this channel, the removed command can no longer be executed.

        You may provide a channel other than the current one.

        Examples:
            !only.remove test
            !only.remove test #lobby
        """

        assert ctx.guild

        if not channel:
            channel = ctx.channel  # type: ignore
            assert channel

        chan_id = str(channel.id)
        guild = str(ctx.guild.id)
        ours = onlies[guild] if guild in onlies else {}
        ourchan = (
            ours[chan_id] if ours is not None and chan_id in ours else None
        )

        if ourchan is None:
            await ctx.send(":person_shrugging: None set.")

            return

        ourchan.remove(command)

        if len(ourchan) == 0:
            del ours[chan_id]
        else:
            ours[chan_id] = ourchan

        if len(ours) == 0:
            del onlies[guild]
        else:
            onlies[guild] = ours

        log.info(f"{ctx.author} removed {command} from {channel} whitelist")
        await ctx.send(":wastebasket: Removed.")

    @command(name="only.list")
    async def list(
        self,
        ctx: Context,
        channel: TextChannel | None = None,
    ):
        """
        List all current channel's whitelisted commands

        You may provide a channel other than the current one.

        Examples:
            !only.list
            !only.list #lobby
        """

        assert ctx.guild

        if not channel:
            channel = ctx.channel  # type: ignore
            assert channel

        chan_id = str(channel.id)
        guild = str(ctx.guild.id)

        if guild not in onlies:
            onlies[guild] = dict()

        ours = onlies[guild]

        if channel not in ours:
            ours[channel] = set([])

        output = "**, **".join(ours.get(chan_id, []))

        if not len(output):
            output = "None"

        log.info(f"{ctx.author} viewed command whitelist for {channel}")
        await ctx.send(f":guard: **{output}**")

    @command(name="only.reset")
    async def reset(
        self,
        ctx: Context,
        channel: TextChannel | None = None,
    ):
        """
        Reset Only whitelist

        Using this command will disable whitelisting behavior and remove the existing whitelist.

        You may provide a channel other than the current one.

        Examples:
            !only.reset
            !only.reset #lobby
        """

        assert ctx.guild

        if not channel:
            channel = ctx.channel  # type: ignore
            assert channel

        chan_id = str(channel.id)
        guild = str(ctx.guild.id)
        ours = onlies[guild] if guild in onlies else {}
        ourchan = (
            ours[chan_id] if ours is not None and chan_id in ours else None
        )

        if ourchan is None:
            await ctx.send(":person_shrugging: None set.")

            return

        del ours[chan_id]

        if len(ours) == 0:
            del onlies[guild]
        else:
            onlies[guild] = ours

        await ctx.send(":boom: Reset.")
        log.info(f"{ctx.author} reset Only whitelist for {channel}")


async def check_only(ctx: Context):
    """Check that command is in the Only whitelist"""

    assert ctx.guild
    assert ctx.command

    if isinstance(ctx.channel, DMChannel):
        # can't whitelist commands via DM, since we need a guild to check
        # settings values
        return True

    guild = str(ctx.guild.id)
    channel = str(ctx.channel.id)
    ours = onlies[guild] if guild in onlies else None
    ourchan = ours[channel] if ours is not None and channel in ours else None

    if ourchan is None:
        # none set for this channel; bail
        return True

    cmd = ctx.command.name

    if cmd not in ourchan and cmd[0:5] != "only.":
        log.debug(
            f"Suppressing non-whitelisted command from {ctx.author}: "
            f"{ctx.command.name} in #{ctx.channel} ({ctx.guild})"
        )

        return False

    return True


async def setup(bot):
    bot.add_check(check_only)
    cog = Only(bot)

    for c in cog.get_commands():
        c.add_check(channel_only)
        c.add_check(require_admin)

    await bot.add_cog(cog)
