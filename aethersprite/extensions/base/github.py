"GitHub URL command"

# 3rd party
from discord.ext.commands import Bot, command

# local
from aethersprite import log


@command(brief="GitHub URL for bot source code, feature requests", pass_context=True)
async def github(ctx):
    """
    This bot is running on Aethersprite, an open source bot software built with discord.py. My source code is available for free. Contributions in the form of code, bug reports, and feature requests are all welcome.

    https://github.com/haliphax/aethersprite
    """

    await ctx.send(
        "For source code, feature requests, and bug reports, visit "
        "https://github.com/haliphax/aethersprite"
    )
    log.info(f"{ctx.author} requested GitHub URL")


async def setup(bot: Bot):
    bot.add_command(github)
