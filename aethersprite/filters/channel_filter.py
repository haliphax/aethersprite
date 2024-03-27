"""Channel setting filter"""

# 3rd party
from discord.ext.commands import Context

# local
from ..common import get_channel_for_id, get_id_for_channel, get_mixed_channels
from .setting_filter import SettingFilter


class ChannelFilter(SettingFilter):
    """Filter used for converting channel names to IDs and back"""

    multiple: bool = False
    """True to allow multiple values"""

    def __init__(self, setting: str, multiple: bool = False):
        super().__init__(setting)
        self.multiple = multiple

    def in_(self, ctx: Context, value: str | None) -> list[int] | None:
        """
        Filter setting input.

        Args:
            ctx: The current context
            value: The incoming value

        Returns:
            The raw setting value (a list of channel IDs)
        """

        if not value:
            return

        channels = get_mixed_channels(value)
        ids = []

        for c in channels:
            id = None

            if c[0] == "":
                id = get_id_for_channel(ctx.guild, c[1])
            else:
                # convert mentions, if any
                id = int(c[0])

            if id is None:
                raise ValueError()

            ids.append(id)

            if not self.multiple:
                break

        return ids

    def out(
        self,
        ctx: Context,
        value: list[int] | None,
    ) -> list[str | None] | str | None:
        """
        Filter setting output.

        Args:
            ctx: The current context
            value: The raw setting value: a list of channel IDs

        Returns:
            The filtered setting value (a list of channel names)
        """

        if value is None:
            return

        channels = (
            [get_channel_for_id(ctx.guild, value)]
            if value is int
            else [get_channel_for_id(ctx.guild, v) for v in value]
        )

        if self.multiple:
            return channels

        if len(channels) > 0:
            return channels[0]

        return None
