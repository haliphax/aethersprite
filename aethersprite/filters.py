"Setting filters module"

# stdlib
import re
# local
from . import log
from .common import (get_channel_for_id, get_id_for_channel, get_id_for_role,
                     get_role_for_id)
from .settings import SettingFilter, settings


class ChannelFilter(SettingFilter):

    "Filter used for converting channel names to IDs and back"

    #: True to allow multiple values
    multiple: bool = True

    def __init__(self, setting: str, multiple: bool = False):
        super().__init__(setting)
        self.multiple = multiple

    def in_(self, ctx, value: str):
        channels = re.findall(r'<#(\d+)> ?|([-_a-zA-Z0-9]+)[, ]*', value.strip())
        log.info(channels)
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

    def out(self, ctx) -> str:
        value = settings[self.setting].get(ctx, raw=True)

        if value is None:
            return

        return [get_channel_for_id(ctx.guild, v) for v in value]

ChannelFilter.in_.__doc__ = SettingFilter.in_.__doc__
ChannelFilter.out.__doc__ = SettingFilter.out.__doc__


class RoleFilter(SettingFilter):

    "Filter used for converting role names to IDs and back"

    #: True to allow multiple values
    multiple: bool = True

    def __init__(self, setting: str, multiple: bool = True):
        super().__init__(setting)
        self.multiple = multiple

    def in_(self, ctx, value: str):
        roles = re.findall(r'<@&(\d+)> ?|([^,]+)[, ]*', value)
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

    def out(self, ctx) -> str:
        value = settings[self.setting].get(ctx, raw=True)

        if value is None:
            return

        return [get_role_for_id(ctx.guild, v) for v in value]

RoleFilter.in_.__doc__ = SettingFilter.in_.__doc__
RoleFilter.out.__doc__ = SettingFilter.out.__doc__
