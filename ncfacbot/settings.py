"Setting module"

# stdlib
import typing
# 3rd party
from sqlitedict import SqliteDict

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

    global settings

    if name in settings:
        raise Exception(f'Setting already exists: {name}')

    settings[name] = Setting(name, default, validator, channel, description)
