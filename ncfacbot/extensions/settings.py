"Settings commands; store, view, and manipulate settings"

# stdlib
import typing
# 3rd party
from discord.ext import commands
from functools import partial
# local
from .. import log
from ..authz import channel_only, require_roles
from ..common import command, THUMBS_DOWN
from ..settings import register, settings

# messages
MSG_NO_SETTING = ':person_shrugging: No such setting exists.'

# authorization decorator
authz = partial(require_roles, setting='settings.adminroles')


class Settings(commands.Cog, name='settings'):

    """
    Settings commands

    View settings, change settings, reset settings, and view settings descriptions.
    """

    def __init__(self, bot):
        self.bot = bot

    @command(name='set')
    @commands.check(authz)
    @commands.check(channel_only)
    async def set(self, ctx, name: typing.Optional[str] = None,
                  value: typing.Optional[str] = None):
        """
        Change/view a setting's value

        If [name] is not provided, a list of all settings (but not their values) will be shown. If [value] is not provided, the setting's current value (and its default) will be shown, instead. Note that channel-dependent settings must be set and viewed in relevant channels.
        """

        if name is None:
            settings_str = '**, **'.join(sorted(settings.keys()))
            await ctx.send(f':gear: All settings: **{settings_str}**')
            log.info(f'{ctx.author} viewed all settings')

            return

        if name not in settings:
            await ctx.send(MSG_NO_SETTING)
            log.warn(f'{ctx.author} attempted to set nonexistent setting: '
                     f'{name}')

            return

        key = ctx.guild.id

        if value is None:
            value = settings[name].get(ctx)
            default = settings[name].default
            await ctx.send(f':gear: `{name} => {repr(value)}` '
                           f'_(Default: {repr(default)})_')
            log.info(f'{ctx.author} viewed setting {name}')
        elif settings[name].set(ctx, value):
            await ctx.send(f':thumbsup: Value updated.')
            log.info(f'{ctx.author} updated setting {name}: {value}')
        else:
            await ctx.send(f':thumbsdown: Error updating value.')
            log.warn(f'{ctx.author} failed to update setting {name}: {value}')

    @command(name='clear')
    @commands.check(authz)
    @commands.check(channel_only)
    async def clear(self, ctx, name):
        "Reset setting <name> to its default value"

        if name not in settings:
            log.warn(f'{ctx.author} attempted to clear nonexistent setting: '
                     f'{name}')
            await ctx.send(MSG_NO_SETTING)

            return

        settings[name].set(ctx, None)
        await ctx.send(':negative_squared_cross_mark: Setting cleared.')
        log.info(f'{ctx.author} cleared setting {name}')

    @command(name='desc')
    @commands.check(authz)
    @commands.check(channel_only)
    async def desc(self, ctx, name):
        "View description of setting <name>"

        if name not in settings:
            await ctx.send(MSG_NO_SETTING)
            log.warn(f'{ctx.author} attempted to view description of '
                     f'nonexistent setting {name}')

            return

        setting = settings[name]

        if setting.description is None:
            await ctx.send(':person_shrugging: No description set.')
        else:
            await ctx.send(f':book: `{setting.name}` '
                           f'_(Channel: **{str(setting.channel)}**)_\n'
                           f'> {setting.description}')

        log.info(f'{ctx.author} viewed description of setting {name}')


def setup(bot):
    # settings
    register('settings.adminroles', None, lambda x: True, False,
             'The server roles that are allowed to administer settings. '
             'Separate multiple values with commas. Administrators and '
             'moderators have de facto access to all commands.')
    bot.add_cog(Settings(bot))
