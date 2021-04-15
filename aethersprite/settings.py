"""
Settings module; interfaced with via
:mod:`aethersprite.extensions.base.settings`

This provides methods by which extension authors can register and use settings
in their code, and end users can manipulate those settings via bot commands
(in the aforementioned `settings` extension).

Examples for registering a setting and getting/changing/resetting its value:

.. note::

    There are commands for doing each of these things already in the base
    extension mentioned above that provide authorization checks, but these are
    just simple examples.

.. code:: python

    from discord.ext.commands import command
    from aethersprite.settings import register, settings

    register('my.setting', 'default value', False, lambda x: True,
             'There are many settings like it, but this one is mine.')

    @command()
    async def check(ctx):
        await ctx.send(settings['my.setting'].get(ctx))

    @command()
    async def change(ctx):
        settings['my.setting'].set(ctx, 'new value')

    @command()
    async def reset(ctx):
        settings['my.setting'].clear(ctx)
"""

# stdlib
from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from .filters import SettingFilter

# 3rd party
from sqlitedict import SqliteDict
# local
from . import data_folder

# TODO cleanup settings for missing servers/channels on startup

#: Setting definitions
settings = {}


class Setting(object):

    "Setting class; represents an individual setting definition"

    # Setting values
    _values = SqliteDict(f'{data_folder}settings.sqlite3', tablename='values',
                         autocommit=True)

    def __init__(self, name: str, default: str, validate: callable,
                 channel: typing.Optional[bool] = False,
                 description: typing.Optional[str] = None,
                 filter: 'SettingFilter' = None):
        if name is None:
            raise ValueError('Name must not be None')

        #: The setting's name
        self.name = name
        #: Default value
        self.default = default
        #: Validator function
        self.validate = validate
        #: If this is a channel (and not a guild) setting
        self.channel = channel
        #: This setting's description
        self.description = description
        #: The filter used to manipulate setting input/output
        self.filter = filter

    def _ctxkey(self, ctx, channel: str = None):
        """
        Get the key to use when storing/accessing the setting.

        :param ctx: The Discord connection context
        :param channel: The channel (if not the same as the context)
        :returns: The composite key
        :rtype: str
        """

        key = str(ctx.guild['id']
                  if isinstance(ctx.guild, dict) else ctx.guild.id)

        if self.channel:
            key += f'#{ctx.channel.id if channel is None else channel}'

        return key

    def set(self, ctx, value: str, raw: bool = False, channel: str = None):
        """
        Change the setting's value.

        :param ctx: The Discord connection context
        :param value: The value to assign (or ``None`` for the default)
        :param raw: Set to True to bypass filtering
        :param channel: The channel (if not the same as the context)
        :returns: Success
        :rtype: bool
        """

        key = self._ctxkey(ctx, channel)
        vals = self._values[key] if key in self._values else {}

        try:
            if not raw and self.filter is not None:
                value = self.filter.in_(ctx, value)
        except ValueError:
            return False

        if value is None:
            vals[self.name] = self.default
        else:
            if not self.validate(value):
                return False

            vals[self.name] = value

        self._values[key] = vals

        return True

    def get(self, ctx, raw: bool = False, channel: str = None):
        """
        Get the setting's value.

        :param ctx: The Discord connection context
        :param raw: Set to True to bypass filtering
        :param channel: The channel (if not the same as the context)
        :returns: The setting's value
        :rtype: str
        """

        key = self._ctxkey(ctx)
        val = self._values[key][self.name] \
                if key in self._values and self.name in self._values[key] \
                else None

        if not raw and self.filter is not None:
            val = self.filter.out(ctx, val)

        return self.default if val is None else val


def register(name: str, default: str, validator: callable,
             channel: typing.Optional[bool] = False,
             description: typing.Optional[str] = None,
             filter: typing.Optional['SettingFilter'] = None):
    """
    Register a setting.

    :param name: The name of the setting
    :param default: The default value if none is provided
    :param validator: The validation function for the setting's value
    :param channel: If this is a channel (and not a guild) setting
    :param filter:
    """

    global settings

    if name in settings:
        raise Exception(f'Setting already exists: {name}')

    settings[name] = Setting(name, default, validator, channel, description,
                             filter=filter)
