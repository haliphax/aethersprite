"Alias cog"

# stdlib
import typing
# 3rd party
from discord.ext.commands import Cog, command
from sqlitedict import SqliteDict
# local
from .. import log
from ..authz import channel_only, require_admin

#: Aliases database
aliases = SqliteDict('alias.sqlite3', tablename='aliases', autocommit=True)


class Alias(Cog, name='alias'):

    "Alias commands; add and remove command aliases"

    def __init__(self, bot):
        self.bot = bot

    @command(name='alias.add')
    async def add(self, ctx, alias, command):
        "Add an alias of <alias> for <command>"

        guild = str(ctx.guild.id)

        if ctx.guild.id not in aliases:
            aliases[guild] = dict()

        als = aliases[guild]

        if alias in als:
            await ctx.send(f':newspaper: Already exists.')

            return

        cmd = ctx.bot.get_command(command)

        if cmd is None:
            await ctx.send(f':scream: No such command!')

            return

        if cmd.aliases is None:
            cmd.aliases = [alias,]
        else:
            cmd.aliases.append(alias)

        ctx.bot.remove_command(command)
        ctx.bot.add_command(cmd)
        als[alias] = command
        aliases[guild] = als
        log.info(f'{ctx.author} added alias {alias} for {command}')
        await ctx.send(f':sunglasses: Done.')

    @command(name='alias.remove')
    async def remove(self, ctx, alias):
        "Remove <alias>"

        guild = str(ctx.guild.id)
        als = aliases[guild] if guild in aliases else None

        if als is None or alias not in als:
            await ctx.send(':person_shrugging: None set.')

            return

        del als[alias]

        if len(als) == 0:
            del aliases[guild]
        else:
            aliases[guild] = als

        cmd = ctx.bot.get_command(alias)

        if cmd is not None \
                and cmd.aliases is not None \
                and alias in cmd.aliases:
            cmd.aliases.remove(alias)

        log.info(f'{ctx.author} removed alias {alias}')
        await ctx.send(':wastebasket: Removed.')

    @command(name='alias.list')
    async def list(self, ctx):
        "List all command aliases"

        guild = str(ctx.guild.id)

        if guild not in aliases:
            aliases[guild] = dict()

        als = aliases[guild]

        output = '**, **'.join([f'`{k} => {als[k]}`' for k in als.keys()])

        if len(output) == 0:
            output = 'None'

        log.info(f'{ctx.author} viewed alias list')
        await ctx.send(f':detective: **{output}**')


def setup(bot):
    cog = Alias(bot)

    for c in cog.get_commands():
        c.add_check(channel_only)
        c.add_check(require_admin)

    bot.add_cog(cog)
