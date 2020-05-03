"Common functions module"

# stdlib
import calendar
from datetime import datetime, timezone
from functools import wraps
from math import ceil, floor
import re
# 3rd party
from discord import DMChannel
from discord.ext.commands import Context

# constants
MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
#: 15 minutes in seconds
FIFTEEN_MINS = 900
#: Thumbs down emoji
THUMBS_DOWN = '\U0001F44E'
#: Formatting string for datetime objects
DATETIME_FORMAT = '%a %Y-%m-%d %H:%M:%S %Z'


def channel_only(f):
    "Decorator for bot commands that should only operate in a channel"

    @wraps(f)
    async def wrap(*args, **kwargs):
        ctx = None

        for a in args:
            if type(a) is Context:
                ctx = a
                break

        if type(ctx.channel) is DMChannel:
            await ctx.send('This command must be used in a channel.')

            return

        return await f(*args, **kwargs)

    return wrap


def get_datetime_chunks(string):
    "Search string for chunks of datetime parameters, like 5d 10h 15m, etc."

    s = re.search(r'.*?(-?\d+)d.*', string)
    days = int(s.groups()[0]) if s else 0
    s = re.search(r'.*?(-?\d+)h.*', string)
    hours = int(s.groups()[0]) if s else 0
    s = re.search(r'.*?(-?\d+)m.*', string)
    minutes = int(s.groups()[0]) if s else 0

    return (days, hours, minutes)


def get_next_tick(n=1):
    "Calculate future tick as datetime in GMT"

    now = calendar.timegm(datetime.now(timezone.utc).timetuple())
    tick_stamp = (now + (n * FIFTEEN_MINS)) - (now % FIFTEEN_MINS)

    return datetime.fromtimestamp(tick_stamp, tz=timezone.utc)


def normalize_username(author):
    "Normalize username for use in messages"

    name = author.name

    if hasattr(author, 'nick') and author.nick is not None:
        name = author.nick

    return name


def seconds_to_str(ts):
    diff = ceil(ts)
    until = ''

    if diff >= DAY:
        until += f'{floor(diff / DAY)} day(s) '
        diff = diff % DAY

    if diff >= HOUR:
        until += f'{floor(diff / HOUR)} hour(s) '
        diff = diff % HOUR

    if diff >= MINUTE:
        until += f'{floor(diff / MINUTE)} minute(s) '
        diff = diff % MINUTE

    if diff > 0:
        until += f'{diff} second(s) '

    return until.strip()
