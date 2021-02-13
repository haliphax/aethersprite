"Setting filters module"

# local
from .common import (get_channel_for_id, get_id_for_channel, get_id_for_role,
                     get_role_for_id)
from .settings import SettingFilter, settings


class ChannelFilter(SettingFilter):

    "Filter used for converting channel names to IDs and back"

    def in_(self, ctx, value: str):
        val = get_id_for_channel(ctx.guild, value)

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
        ids = [get_id_for_role(ctx.guild, v) for v in value.split(',')]

        for id in ids:
            if id is None:
                raise ValueError()

        return ids

    def out(self, ctx) -> str:
        value = settings[self.setting].get(ctx, raw=True)

        if value is None:
            return

        return ', '.join([get_role_for_id(ctx.guild, v) for v in value])

RoleFilter.in_.__doc__ = SettingFilter.in_.__doc__
RoleFilter.out.__doc__ = SettingFilter.out.__doc__
