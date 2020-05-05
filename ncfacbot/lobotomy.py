"Lobotomy module"

# 3rd party
from discord import DMChannel
from discord.ext.commands import DisabledCommand
from sqlitedict import SqliteDict
# local
from . import log

#: Lobotomies database
lobotomies = SqliteDict('lobotomy.sqlite3', tablename='lobotomies',
                        autocommit=True)


async def check_lobotomy(ctx):
    "Check that command has not been lobotomized before allowing execution."

    if type(ctx.channel) is DMChannel:
        # can't lobotomize commands via DM, since we need a guild to check
        # settings values
        return

    guild = str(ctx.guild.id)

    if guild not in lobotomies:
        # none set for this guild; bail
        return True

    keys = (ctx.command.name, f'{ctx.command.name}#{ctx.channel.id}')

    for k in keys:
        if k in lobotomies[guild]:
            log.warn(f'Suppressing lobotomized command from '
                     f'{ctx.author}: {ctx.command.name} in '
                     f'#{ctx.channel.name}')

            return False

    return True
