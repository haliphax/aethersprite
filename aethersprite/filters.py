"Setting filters module"

# stdlib
import re
# local
from .common import (get_channel_for_id, get_id_for_channel, get_id_for_role,
                     get_role_for_id)
from .settings import SettingFilter, settings


class ChannelFilter(SettingFilter):

    "Filter used for converting channel names to IDs and back"

    def in_(self, ctx, value: str):
        match = re.match(r'^<#(\d+)>$', value.strip())
        val = None

        if match is None:
            val = get_id_for_channel(ctx.guild, value)
        else:
            val = int(match.groups()[0])

        if val is None:
            raise ValueError()

        return val

    def out(self, ctx) -> str:
        val = settings[self.setting].get(ctx, raw=True)
        val = get_channel_for_id(ctx.guild, val)

        return val

ChannelFilter.in_.__doc__ = SettingFilter.in_.__doc__
ChannelFilter.out.__doc__ = SettingFilter.out.__doc__


class RoleFilter(SettingFilter):

    "Filter used for converting role names to IDs and back"

    def in_(self, ctx, value: str):
        roles = [v.strip() for v in value.split(',')]
        ids = []

        for r in roles:
            match = re.match(r'^<@&(\d+)>$', r)

            if match is None:
                id = get_id_for_role(ctx.guild, r)
            else:
                id = int(match.groups()[0])

            if id is None:
                raise ValueError(r)

            ids.append(id)

        return ids

    def out(self, ctx) -> str:
        value = settings[self.setting].get(ctx, raw=True)

        if value is None:
            return

        return ', '.join([get_role_for_id(ctx.guild, v) for v in value])

RoleFilter.in_.__doc__ = SettingFilter.in_.__doc__
RoleFilter.out.__doc__ = SettingFilter.out.__doc__
