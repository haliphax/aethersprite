"""Alias cog"""

# 3rd party
from discord.ext.commands import Bot, Cog, command, Context
from sqlitedict import SqliteDict

# local
from aethersprite import data_folder, log
from aethersprite.authz import channel_only, require_admin

aliases = SqliteDict(
    f"{data_folder}alias.sqlite3", tablename="aliases", autocommit=True
)
"""Aliases database"""

bot: Bot


class Alias(Cog):
    """Alias commands; add and remove command aliases"""

    @staticmethod
    def get_aliases(ctx: Context, cmd: str):
        """Get aliases for the given command and context."""

        assert ctx.guild
        mylist = list()
        guild = str(ctx.guild.id)

        if guild not in aliases:
            return mylist

        glist = aliases[guild]

        for k in glist:
            if glist[k] == cmd:
                mylist.append(k)

        return mylist

    def __init__(self, bot):
        self.bot = bot
        self.aliases = aliases

    @command(name="alias.add")
    async def add(self, ctx: Context, alias: str, command: str):
        """Add an alias of <alias> for <command>"""

        assert ctx.guild
        guild = str(ctx.guild.id)

        if ctx.guild.id not in aliases:
            aliases[guild] = dict()

        als = aliases[guild]

        if alias in als:
            await ctx.send(":newspaper: Already exists.")

            return

        cmd = bot.get_command(command)

        if cmd is None:
            await ctx.send(":scream: No such command!")

            return

        als[alias] = command
        aliases[guild] = als
        log.info(f"{ctx.author} added alias {alias} for {command}")
        await ctx.send(":sunglasses: Done.")

    @command(name="alias.remove")
    async def remove(self, ctx: Context, alias: str):
        """Remove <alias>"""

        assert ctx.guild
        guild = str(ctx.guild.id)
        als = aliases[guild] if guild in aliases else None

        if als is None or alias not in als:
            await ctx.send(":person_shrugging: None set.")

            return

        del als[alias]

        if len(als) == 0:
            del aliases[guild]
        else:
            aliases[guild] = als

        log.info(f"{ctx.author} removed alias {alias}")
        await ctx.send(":wastebasket: Removed.")

    @command(name="alias.list")
    async def list(self, ctx: Context):
        """List all command aliases"""

        assert ctx.guild
        guild = str(ctx.guild.id)

        if guild not in aliases:
            aliases[guild] = dict()

        als = aliases[guild]
        output = ", ".join([f"`{k}` => `{als[k]}`" for k in als.keys()])

        if len(output) == 0:
            output = "None"

        log.info(f"{ctx.author} viewed alias list")
        await ctx.send(f":detective: **{output}**")


async def setup(bot_: Bot):
    global bot

    bot = bot_
    cog = Alias(bot)

    for c in cog.get_commands():
        c.add_check(channel_only)
        c.add_check(require_admin)

    await bot.add_cog(cog)
