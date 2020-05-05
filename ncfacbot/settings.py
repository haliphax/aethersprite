"Setting module"

# stdlib
from functools import wraps
from os import environ
import typing
# 3rd party
from discord.ext.commands import Context
from sqlitedict import SqliteDict
# local
from . import log
from .common import THUMBS_DOWN

# TODO cleanup settings for missing servers/channels on startup

#: Setting definitions
settings = {}


class Setting(object):

    "Setting class; represents an individual setting definition"

    # Setting values
    _values = SqliteDict('settings.sqlite3', tablename='values',
                         autocommit=True)

    def __init__(self, name: str, default: str, validate: callable,
                 channel: typing.Optional[bool] = False,
                 description: typing.Optional[str] = None):
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

    def _ctxkey(self, ctx):
        """
        Get the key to use when storing/accessing the setting.

        :param ctx: The Discord connection context
        :returns: The composite key
        :rtype: str
        """

        key = ctx.guild.id

        if self.channel:
            key += '#' + ctx.channel.id

        return key

    def set(self, ctx, value: str):
        """
        Change the setting's value.

        :param ctx: The Discord connection context
        :param value: The value to assign (or ``None`` for the default)
        :returns: Success
        :rtype: bool
        """

        key = self._ctxkey(ctx)
        vals = self._values[key] if key in self._values else {}

        if value is None:
            vals[self.name] = self.default
        else:
            if not self.validate(value):
                return False

            vals[self.name] = value

        self._values[key] = vals

        return True

    def get(self, ctx):
        """
        Get the setting's value.

        :param ctx: The Discord connection context
        :returns: The setting's value
        :rtype: str
        """

        key = self._ctxkey(ctx)
        val = self._values[key][self.name] \
                if key in self._values and self.name in self._values[key] \
                else None

        return self.default if val is None else val


def register(name: str, default: str, validator: callable,
             channel: typing.Optional[bool] = False,
             description: typing.Optional[str] = None):
    """
    Register a setting.

    :param name: The name of the setting
    :param default: The default value if none is provided
    :param validator: The validation function for the setting's value
    :param channel: If this is a channel (and not a guild) setting
    """

    if name in settings:
        raise Exception(f'Setting already exists: {name}')

    settings[name] = Setting(name, default, validator, channel, description)


def require_admin(f: callable):
    "Decorator for requiring admin/mod privileges to execute a command."

    @wraps(f)
    async def wrap(*args, **kwargs):
        ctx = None

        for a in args:
            if type(a) is Context:
                ctx = a

                break

        perms = ctx.author.permissions_in(ctx.channel)

        if perms.administrator or perms.manage_channels or perms.manage_guild \
                or (environ.get('NCFACBOT_OWNER', '') == str(ctx.author)):
            return await f(*args, **kwargs)

    return wrap


def require_roles(f: callable, setting):
    """
    Decorator for requiring particular roles (loaded from the given setting) to
    execute a command. For more than one setting (if ``setting`` is a
    list/tuple), the aggregate list will be used. Membership in at least one of
    the roles pulled from the settings is required to pass the filter.

    :param setting: The name of the setting to pull the roles from
    :type setting: str or list or tuple
    """

    @wraps(f)
    async def wrap(*args, **kwargs):
        ctx = None

        for a in args:
            if type(a) is Context:
                ctx = a

                break

        perms = ctx.author.permissions_in(ctx.channel)
        pass_ = False

        if perms.administrator or perms.manage_channels or perms.manage_guild \
                or (environ.get('NCFACBOT_OWNER', '') == str(ctx.author)):
            # Superusers get a pass
            pass_ = True

        values = None
        kind = type(setting)

        if kind == str:
            values = settings[setting].get(ctx)
        elif kind in (list, tuple):
            names = []

            for s in setting:
                val = settings[s].get(ctx)

                if val is not None:
                    names.append(val)

            values = ','.join(names)
        else:
            raise ValueError('setting must be str, list, or tuple')

        if values is None:
            values = []

        roles = [s.strip().lower() for s in values.split(',')] \
                if len(values) else tuple()

        if len(roles) and len([r for r in ctx.author.roles
                               if r.name.lower() in roles]):
            pass_ = True

        if not pass_:
            await ctx.message.add_reaction(POLICE_OFFICER)
            log.warn(f'{ctx.author} attempted to access unauthorized '
                     f'command {f.__name__}')

            return

        return await f(*args, **kwargs)

    return wrap
