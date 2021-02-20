"Only cog"

# stdlib
import typing
# 3rd party
from discord import DMChannel
from discord.ext.commands import Cog, command
from sqlitedict import SqliteDict
# local
from aethersprite import log
from aethersprite.authz import channel_only, require_admin

#: Only whitelist database
onlies = SqliteDict('only.sqlite3', tablename='onlies', autocommit=True)


class Only(Cog, name='only'):

    "Only commands; disable all commands except for those in a whitelist"

    def __init__(self, bot):
        self.bot = bot

    @command(name='only.add')
    async def add(self, ctx, command):
        """
        Add the given command to the Only whitelist

        Enables <command> in this channel.
        """

        guild = str(ctx.guild.id)
        channel = str(ctx.channel.id)

        if guild not in onlies:
            onlies[guild] = dict()

        ours = onlies[guild]

        if channel not in ours:
            ours[channel] = set([])

        ourchan = ours[channel]

        if command in ourchan:
            await ctx.send(f':newspaper: Already done.')

            return

        ourchan.add(command)
        ours[channel] = ourchan
        onlies[guild] = ours
        log.info(f'{ctx.author} added {command} to {ctx.channel} whitelist')
        await ctx.send(f':shield: Done.')

    @command(name='only.remove')
    async def remove(self, ctx, command):
        """
        Remove the given command from the Only whitelist

        If whitelisting is enabled for this channel, the removed command can no longer be executed.
        """

        guild = str(ctx.guild.id)
        channel = str(ctx.channel.id)
        ours = onlies[guild] if guild in onlies else None
        ourchan = ours[channel] \
                if ours is not None and channel in ours else None

        if ourchan is None:
            await ctx.send(':person_shrugging: None set.')

            return

        ourchan.remove(command)

        if len(ourchan) == 0:
            del ours[channel]
        else:
            ours[channel] = ourchan

        if len(ours) == 0:
            del onlies[guild]
        else:
            onlies[guild] = ours

        log.info(f'{ctx.author} removed {command} from {ctx.channel} '
                 'whitelist')
        await ctx.send(':wastebasket: Removed.')

    @command(name='only.list')
    async def list(self, ctx, server: typing.Optional[bool] = False):
        "List all current channel's whitelisted commands"

        guild = str(ctx.guild.id)
        channel = str(ctx.channel.id)

        if guild not in onlies:
            onlies[guild] = dict()

        ours = onlies[guild]

        if channel not in ours:
            ours[channel] = set([])

        output = '**, **'.join(ours[channel])

        if not len(output):
            output = 'None'

        log.info(f'{ctx.author} viewed command whitelist for {ctx.channel}')
        await ctx.send(f':guard: **{output}**')

    @command(name='only.reset')
    async def reset(self, ctx):
        """
        Reset Only whitelist

        Using this command will disable whitelisting behavior and remove the existing whitelist.
        """

        guild = str(ctx.guild.id)
        channel = str(ctx.channel.id)
        ours = onlies[guild] if guild in onlies else None
        ourchan = ours[channel] \
                if ours is not None and channel in ours else None

        if ourchan is None:
            await ctx.send(':person_shrugging: None set.')

            return

        del ours[channel]

        if len(ours) == 0:
            del onlies[guild]
        else:
            onlies[guild] = ours

        await ctx.send(':boom: Reset.')
        log.info(f'{ctx.author} reset Only whitelist for {ctx.channel}')


async def check_only(ctx):
    "Check that command is in the Only whitelist"

    if isinstance(ctx.channel, DMChannel):
        # can't whitelist commands via DM, since we need a guild to check
        # settings values
        return True

    guild = str(ctx.guild.id)
    channel = str(ctx.channel.id)
    ours = onlies[guild] if guild in onlies else None
    ourchan = ours[channel] \
            if ours is not None and channel in ours else None

    if ourchan is None:
        # none set for this channel; bail
        return True

    cmd = ctx.command.name

    if cmd not in ourchan and cmd[0:5] != 'only.':
        log.debug(f'Suppressing non-whitelisted command from {ctx.author}: '
                  f'{ctx.command.name} in #{ctx.channel} ({ctx.guild})')

        return False

    return True


def setup(bot):
    bot.add_check(check_only)
    cog = Only(bot)

    for c in cog.get_commands():
        c.add_check(channel_only)
        c.add_check(require_admin)

    bot.add_cog(cog)
