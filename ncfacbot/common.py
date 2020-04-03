"Common functions module"

# stdlib
import calendar
from datetime import datetime, timezone
from math import floor

# constants
FIVE_MINS = 300
FIFTEEN_MINS = 900

#: :thumbsdown: emoji
THUMBS_DOWN = '\U0001F44E'


def get_next_tick(n=1):
    "Calculate future tick as datetime in GMT"

    now = calendar.timegm(datetime.now(timezone.utc).timetuple())
    tick_stamp = (now + (n * FIFTEEN_MINS)) - (now % FIFTEEN_MINS)
    return datetime.fromtimestamp(tick_stamp, tz=timezone.utc)


def normalize_username(author):
    "Normalize username for use in messages"

    name = author.name

    if author.nick is not None:
        name = author.nick
