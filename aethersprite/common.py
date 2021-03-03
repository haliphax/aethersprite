"Common functions module"

# stdlib
from collections import namedtuple
from datetime import datetime, timezone
from math import ceil, floor
import re
from typing import Optional, Tuple

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


def get_mixed_channels(value: str) -> Tuple[Tuple[str, str]]:
    """
    Return a series of group pairs matched from the provided value. The first
    element in each pair will be the channel ID if the match was a mention;
    it will be empty otherwise. The second element in each pair will be the
    plain text of the string token; it will be empty otherwise.

    :param value: The value to match against
    :returns: A series of group pairs (channel ID, channel text)
    """

    return re.findall(r'<#(\d+)> ?|([-_a-zA-Z0-9]+)[, ]*', value.strip())


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


def get_mixed_roles(value: str) -> Tuple[Tuple[str, str]]:
    """
    Return a series of group pairs matched from the provided value. The first
    element in each pair will be the role ID if the match was a mention;
    it will be empty otherwise. The second element in each pair will be the
    plain text of the string token; it will be empty otherwise.

    :param value: The value to match against
    :returns: A series of group pairs (role ID, role text)
    """

    return re.findall(r'<@&(\d+)> ?|([^,]+)[, ]*', value.strip())


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
