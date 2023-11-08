"""Nick command module"""

# 3rd party
from discord.ext.commands import check, command, Context

# local
from aethersprite import log
from aethersprite.authz import channel_only, require_admin


@command()
@check(require_admin)
@check(channel_only)
async def nick(ctx: Context, *, nick: str):
    """Change the bot's nickname on this server"""

    assert ctx.guild
    await ctx.guild.me.edit(nick=nick)
    await ctx.send(":thumbsup:")
    log.info(f"{ctx.author} set bot nickname to {nick}")


async def setup(bot):
    bot.add_command(nick)
