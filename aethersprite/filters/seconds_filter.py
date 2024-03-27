"""Seconds setting filter"""

# 3rd party
from discord.ext.commands import Context

# local
from ..common import get_timespan_chunks, seconds_to_str
from .setting_filter import SettingFilter


class SecondsFilter(SettingFilter):
    """Filter used for converting strings to number of seconds values"""

    def __init__(self, setting: str):
        super().__init__(setting)

    def in_(self, ctx: Context, value: str | None) -> int | None:
        """
        Filter setting input.

        Args:
            ctx: The current context
            value: The incoming value

        Returns:
            The raw setting value (an integer)
        """

        if not value:
            return

        try:
            return int(value)
        except ValueError:
            days, hours, minutes = get_timespan_chunks(value)
            return minutes * 60 + hours * 3600 + days * 86400

    def out(
        self,
        ctx: Context,
        value: int | None,
    ) -> str | None:
        """
        Filter setting output.

        Args:
            ctx: The current context
            value: The raw setting value (an integer)

        Returns:
            The filtered setting value (days, hours, minutes)
        """

        if not value:
            return

        return seconds_to_str(value)
