"Nick command module"

# stdlib
from functools import partial
# 3rd party
from discord.ext import commands
# local
from .. import log
from ..common import command, channel_only
from ..settings import require_admin


@command()
@commands.check(require_admin)
@commands.check(channel_only)
async def nick(ctx, *, nick):
    "Change the bot's nickname on this server"

    await ctx.guild.me.edit(nick=nick)
    await ctx.send(':thumbsup:')
    log.info(f'{ctx.author} set bot nickname to {nick}')


def setup(bot):
    bot.add_command(nick)
