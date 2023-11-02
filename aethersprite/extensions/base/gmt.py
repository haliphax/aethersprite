"GMT time check and offset command"

# stdlib
from datetime import datetime, timedelta
import typing

# 3rd party
from discord.ext.commands import Bot, command, Context
from pytz import timezone

# local
from aethersprite import log
from aethersprite.common import DATETIME_FORMAT, get_timespan_chunks


async def _time(ctx: Context, tz: str, offset: str | None):
    delta = get_timespan_chunks(offset) if offset else (0, 0, 0)
    days, hours, minutes = delta
    thetime = datetime.utcnow().astimezone(timezone(tz)) + timedelta(
        days=days, hours=hours, minutes=minutes
    )
    offset_str = thetime.strftime(DATETIME_FORMAT)
    await ctx.send(f":clock: {offset_str}")
    log.info(f"{ctx.author} requested {tz} offset of {delta}: {offset_str}")


@command(brief="Get current time or offset in GMT")
async def gmt(ctx: Context, *, offset: typing.Optional[str]):
    """
    Get current time in GMT or offset by days, hours, and minutes.

    To get the current time, no arguments are necessary. To get offset time (e.g. 5 hours from now), provide values for days, hours, or minutes. For offsets in the past, use negative numbers.

    Example: !gmt 3d 6h 17m  <-- would request an offset of 3 days, 6 hours, 17 minutes

    Arguments aren't validated, so anything goes... but please be reasonable. The command will silently fail if you choose an offset the bot can't process.
    """

    await _time(ctx, "Etc/GMT")


@command(brief="Get current time or offset in UTC")
async def utc(ctx: Context, *, offset: typing.Optional[str]):
    """
    Get current time in UTC or offset by days, hours, and minutes.

    To get the current time, no arguments are necessary. To get offset time (e.g. 5 hours from now), provide values for days, hours, or minutes. For offsets in the past, use negative numbers.

    Example: !utc 3d 6h 17m  <-- would request an offset of 3 days, 6 hours, 17 minutes

    Arguments aren't validated, so anything goes... but please be reasonable. The command will silently fail if you choose an offset the bot can't process.
    """

    await _time(ctx, "Etc/UTC")


async def setup(bot: Bot):
    bot.add_command(gmt)
    bot.add_command(utc)
