"""Setting filters module"""

# stdlib
from typing import Any

# 3rd party
from discord.ext.commands import Context

# local
from .common import (
    get_channel_for_id,
    get_id_for_channel,
    get_id_for_role,
    get_mixed_channels,
    get_mixed_roles,
    get_role_for_id,
)


class SettingFilter(object):

    """A class with methods for filtering a setting's input and output"""

    setting: str | None = None
    """The name of the setting to filter"""

    def __init__(self, setting: str):
        self.setting = setting

    def in_(self, ctx: Context, value: str | None) -> Any | None:
        """
        Must override; input filter method.

        Args:
            ctx: The current context
            value: The incoming value

        Returns:
            The raw setting value(s), for reference
        """

        raise NotImplementedError()

    def out(self, ctx: Context, value: Any) -> Any | None:
        """
        Must override; output filter method.

        Args:
            ctx: The current context
            value: The raw setting value

        Returns:
            The filtered setting value(s)
        """

        raise NotImplementedError()


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
        value: list[int],
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


class RoleFilter(SettingFilter):

    """Filter used for converting role names to IDs and back"""

    multiple: bool = True
    """True to allow multiple values"""

    def __init__(self, setting: str, multiple: bool = True):
        super().__init__(setting)
        self.multiple = multiple

    def in_(self, ctx: Context, value: str | None) -> list[int] | None:
        """
        Filter setting input.

        Args:
            ctx: The current context
            value: The incoming value

        Returns:
            The raw setting value (a list of role IDs)
        """

        if not value:
            return

        roles = get_mixed_roles(value)
        ids = []

        for r in roles:
            id = None

            if r[0] == "":
                id = get_id_for_role(ctx.guild, r[1])
            else:
                # convert mentions, if any
                id = int(r[0])

            if id is None:
                raise ValueError(r)

            ids.append(id)

            if not self.multiple:
                break

        return ids

    def out(
        self,
        ctx: Context,
        value: list[int],
    ) -> list[str | None] | str | None:
        """
        Filter setting output.

        Args:
            ctx: The current context
            value: The raw setting value: a list of role IDs

        Returns:
            The filtered setting value (a list of role names)
        """

        if value is None:
            return

        roles = [get_role_for_id(ctx.guild, v) for v in value]

        if self.multiple:
            return roles

        if len(roles) > 0:
            return roles[0]

        return None
