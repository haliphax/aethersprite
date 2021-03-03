"Setting filters module"

# stdlib
import re
from typing import Any, List
# 3rd party
from discord.ext.commands import Context
# local
from .common import (get_channel_for_id, get_id_for_channel, get_id_for_role,
                     get_mixed_channels, get_mixed_roles, get_role_for_id)


class SettingFilter(object):

    "A class with methods for filtering a setting's input and output"

    #: The name of the setting to filter
    setting: str = None

    def __init__(self, setting):
        self.setting = setting

    def in_(self, ctx: Context, value: str) -> None:
        """
        Must override; input filter method.

        :param ctx: The current context
        :param value: The incoming value
        """

        raise NotImplementedError()

    def out(self, ctx: Context, value: Any) -> Any:
        """
        Must override; output filter method.

        :param ctx: The current context
        :param value: The raw setting value
        :returns: The filtered setting value
        """

        raise NotImplementedError()


class ChannelFilter(SettingFilter):

    "Filter used for converting channel names to IDs and back"

    #: True to allow multiple values
    multiple: bool = True

    def __init__(self, setting: str, multiple: bool = False):
        super().__init__(setting)
        self.multiple = multiple

    def in_(self, ctx: Context, value: str) -> None:
        """
        Filter setting input.

        :param ctx: The current context
        :param value: The incoming value
        """

        channels = get_mixed_channels(value)
        ids = []

        for c in channels:
            id = None

            if c[0] == '':
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

    def out(self, ctx: Context, value: List[int]) -> List[str]:
        """
        Filter setting output.

        :param ctx: The current context
        :param value: The raw setting value: a list of channel IDs
        :returns: The filtered setting value: a list of channel names
        """

        if value is None:
            return

        return [get_channel_for_id(ctx.guild, v) for v in value]


class RoleFilter(SettingFilter):

    "Filter used for converting role names to IDs and back"

    #: True to allow multiple values
    multiple: bool = True

    def __init__(self, setting: str, multiple: bool = True):
        super().__init__(setting)
        self.multiple = multiple

    def in_(self, ctx: Context, value: str) -> None:
        """
        Filter setting input.

        :param ctx: The current context
        :param value: The incoming value
        """

        roles = get_mixed_roles(value)
        ids = []

        for r in roles:
            id = None

            if r[0] == '':
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

    def out(self, ctx: Context, value: List[int]) -> List[str]:
        """
        Filter setting output.

        :param ctx: The current context
        :param value: The raw setting value: a list of role IDs
        :returns: The filtered setting value: a list of role names
        """

        if value is None:
            return

        return [get_role_for_id(ctx.guild, v) for v in value]
