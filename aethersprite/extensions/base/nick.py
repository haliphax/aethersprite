"Nick command module"

# 3rd party
from discord.ext.commands import check, command
# local
from aethersprite import log
from aethersprite.authz import channel_only, require_admin


@command()
@check(require_admin)
@check(channel_only)
async def nick(ctx, *, nick):
    "Change the bot's nickname on this server"

    await ctx.guild.me.edit(nick=nick)
    await ctx.send(':thumbsup:')
    log.info(f'{ctx.author} set bot nickname to {nick}')


def setup(bot):
    bot.add_command(nick)
