"Setting filters module"

# local
from . import log
from .common import get_channel_for_id, get_id_for_channel
from .settings import SettingFilter, settings


class ChannelFilter(SettingFilter):

    "Filter used for converting channel names to IDs and back"

    def in_(self, ctx, value: str):
        val = get_id_for_channel(ctx.guild, value)

        return val

    def out(self, ctx) -> str:
        val = settings[self.setting].get(ctx, raw=True)
        val = get_channel_for_id(ctx.guild, val)

        return val

ChannelFilter.in_.__doc__ = SettingFilter.in_.__doc__
ChannelFilter.out.__doc__ = SettingFilter.out.__doc__
