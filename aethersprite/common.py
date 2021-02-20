"Common functions module"

# stdlib
import calendar
from collections import namedtuple
from datetime import datetime, timezone
from math import ceil, floor
import re
from typing import Optional

# constants
#: One minute in seconds
MINUTE = 60
#: One hour in seconds
HOUR = MINUTE * 60
#: One day in seconds
DAY = HOUR * 24
#: 15 minutes in seconds
FIFTEEN_MINS = MINUTE * 15
#: Thumbs down emoji
THUMBS_DOWN = '\U0001F44E'
#: Police officer emoji
POLICE_OFFICER = '\U0001F46E'
#: Formatting string for datetime objects
DATETIME_FORMAT = '%a %Y-%m-%d %H:%M:%S %Z'

# structs
#: Fake a context for use in certain functions that expect one
FakeContext = namedtuple('FakeContext', ('guild',))


class HandlerCollection:

    "Static collection of handlers; to be inherited from"

    _handlers: Optional[set] = None
    handlers: Optional[set] = None

    def __init__(self):
        raise RuntimeError('Singleton collection')

    @classmethod
    def add(cls, handler):
        "Add handler to collection."

        if cls.handlers is None:
            cls.handlers = set([])
            cls._handlers = set([])

        if handler.__name__ in set(cls._handlers):
            return

        cls._handlers.add(handler.__name__)
        cls.handlers.add(handler)


class MemberJoinHandlers(HandlerCollection):

    "on_member_join handlers"


class ReadyHandlers(HandlerCollection):

    "on_ready handlers"


def get_channel_for_id(guild, id: int) -> str:
    """
    Return channel name for given guild and channel ID.

    :param guild: The guild object to search
    :param id: The channel ID to search for
    :returns: The name of the channel
    """

    chans = [c.name for c in guild.channels if c.id == id]

    return chans[0] if len(chans) else None


def get_id_for_channel(guild, channel: str) -> int:
    """
    Return channel ID for given guild and channel name.

    :param guild: The guild object to search
    :param channel: The channel to search for
    :returns: The ID of the channel
    """

    channel = channel.lower() if channel is not None else channel
    ids = [c.id for c in guild.channels if c.name.lower() == channel]

    return ids[0] if len(ids) else None


def get_id_for_role(guild, role: str) -> int:
    """
    Return role ID for given guild and role name.

    :param guild: The guild object to search
    :param role: The role to search for
    :returns: The ID of the role
    """

    role = role.lower() if role is not None else role
    ids = [c.id for c in guild.roles if c.name.lower() == role]

    return ids[0] if len(ids) else None


def get_role_for_id(guild, id: int) -> str:
    """
    Return role name for given guild and role ID.

    :param guild: The guild object to search
    :param id: The role ID to search for
    :returns: The name of the role
    """

    roles = [c.name for c in guild.roles if c.id == id]

    return roles[0] if len(roles) else None


def get_timespan_chunks(string: str):
    """
    Search string for chunks of timespan parameters, like 5d 10h 15m, etc.

    :param string: The string to search
    :returns: ``(days: int, hours: int, minutes: int)``
    :rtype: tuple
    """

    s = re.search(r'.*?(-?\d+)d.*', string)
    days = int(s.groups()[0]) if s else 0
    s = re.search(r'.*?(-?\d+)h.*', string)
    hours = int(s.groups()[0]) if s else 0
    s = re.search(r'.*?(-?\d+)m.*', string)
    minutes = int(s.groups()[0]) if s else 0

    return (days, hours, minutes)


def get_next_tick(n=1):
    """
    Calculate future tick as datetime in GMT.

    :param n: The number of ticks forward to calculate
    :type n: int
    :returns: The time of the calculated tick
    :rtype: datetime
    """

    now = calendar.timegm(datetime.now(timezone.utc).timetuple())
    tick_stamp = (now + (n * FIFTEEN_MINS)) - (now % FIFTEEN_MINS)

    return datetime.fromtimestamp(tick_stamp, tz=timezone.utc)


def handle_member_join(f):
    "on_member_join event handler decorator"

    MemberJoinHandlers.add(f)

    return f


def handle_ready(f):
    """
    Decorator to add function to list of handlers to run for the ``on_ready``
    event. The first argument of the function (not counting ``self`` if the
    function is a method) will be provided with a reference to the bot. To
    decorate a method, assign the handler during ``__init__``.

    .. code:: python

        from discord.ext.commands import Cog
        from aethersprite.common import startup

        class SomeClass(Cog):
            def __init__(self, bot):
                self.bot = bot
                self.on_ready = startup(self.on_ready)

            def on_ready(self, _):
                # don't care about the bot parameter here, but still have to include it
                # to avoid exceptions
                pass

        @startup
        def on_ready(bot):
            # since we're not a Cog, we need the bot reference to do stuff
            pass
    """

    ReadyHandlers.add(f)

    return f


def seconds_to_str(ts):
    """
    Convert a span of seconds into a human-readable format (e.g. "5 days
    8 hours 1 minute 36 seconds").

    :param ts: The span to convert
    :type ts: int
    :returns: The human-readable representation
    :rtype: str
    """

    seconds = ceil(ts)
    until = []

    if seconds >= DAY:
        days = floor(seconds / DAY)
        until.append(f'{days} day{"s" if days > 1 else ""}')
        seconds = seconds % DAY

    if seconds >= HOUR:
        hours = floor(seconds / HOUR)
        until.append(f'{hours} hour{"s" if hours > 1 else ""}')
        seconds = seconds % HOUR

    if seconds >= MINUTE:
        minutes = floor(seconds / MINUTE)
        until.append(f'{minutes} minute{"s" if minutes > 1 else ""}')
        seconds = seconds % MINUTE

    if seconds > 0:
        until.append(f'{seconds} second{"s" if seconds > 1 else ""}')

    return ', '.join(until)
