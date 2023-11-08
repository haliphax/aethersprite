"""
Settings module; interfaced with via `aethersprite.extensions.base.settings`

This provides methods by which extension authors can register and use settings
in their code, and end users can manipulate those settings via bot commands
(in the aforementioned `settings` extension).

Examples for registering a setting and getting/changing/resetting its value:

> There are commands for doing each of these things already in the base
> extension mentioned above that provide authorization checks, but these are
> just simple examples.

```python
from discord.ext.commands import command
from aethersprite.settings import register, settings

register("my.setting", "default value", False, lambda x: True,
         "There are many settings like it, but this one is mine.")

@command()
async def check(ctx):
    await ctx.send(settings["my.setting"].get(ctx))

@command()
async def change(ctx):
    settings["my.setting"].set(ctx, "new value")

@command()
async def reset(ctx):
    settings["my.setting"].clear(ctx)
```
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

settings = {}
"""Setting definitions"""


class Setting(object):

    """Setting class; represents an individual setting definition"""

    # Setting values
    _values = SqliteDict(
        f"{data_folder}settings.sqlite3", tablename="values", autocommit=True
    )

    def __init__(
        self,
        name: str,
        default: str | None,
        validate: typing.Callable,
        channel: bool = False,
        description: str | None = None,
        filter: "SettingFilter" | None = None,
    ):
        if name is None:
            raise ValueError("Name must not be None")

        self.name = name
        """The setting's name"""

        self.default = default
        """Default value"""

        self.validate = validate
        """Validator function"""

        self.channel = channel
        """If this is a channel (and not a guild) setting"""

        self.description = description
        """This setting's description"""

        self.filter = filter
        """The filter used to manipulate setting input/output"""

    def _ctxkey(self, ctx, channel: str | None = None) -> str:
        """
        Get the key to use when storing/accessing the setting.

        Args:
            ctx: The Discord connection context
            channel: The channel (if not the same as the context)

        Returns:
            The composite key
        """

        key = str(
            ctx.guild["id"] if isinstance(ctx.guild, dict) else ctx.guild.id
        )

        if self.channel:
            key += f"#{ctx.channel.id if channel is None else channel}"

        return key

    def set(
        self,
        ctx,
        value: str,
        raw: bool = False,
        channel: str | None = None,
    ) -> bool:
        """
        Change the setting's value.

        Args:
            ctx: The Discord connection context
            value: The value to assign (or ``None`` for the default)
            raw: Set to True to bypass filtering
            channel: The channel (if not the same as the context)

        Returns:
            Success
        """

        key = self._ctxkey(ctx, channel)
        vals = self._values[key] if key in self._values else {}

        try:
            if not raw and self.filter is not None:
                filtered = self.filter.in_(ctx, value)

                if not filtered:
                    return False

                value = filtered
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

    def get(self, ctx, raw: bool = False) -> str | None:
        """
        Get the setting's value.

        Args:
            ctx: The Discord connection context
            raw: Set to True to bypass filtering
            channel: The channel (if not the same as the context)

        Returns:
            The setting's value
        """

        key = self._ctxkey(ctx)
        val = (
            self._values[key][self.name]
            if key in self._values and self.name in self._values[key]
            else None
        )

        if not raw and self.filter is not None:
            val = self.filter.out(ctx, val)

        return self.default if val is None else val


def register(
    name: str,
    default: typing.Any | None,
    validator: typing.Callable,
    channel: bool = False,
    description: str | None = None,
    filter: "SettingFilter" | None = None,
):
    """
    Register a setting.

    Args:
        name: The name of the setting
        default: The default value if none is provided
        validator: The validation function for the setting's value
        channel: If this is a channel (and not a guild) setting
        filter: The filter to use for setting/getting values
    """

    global settings

    if name in settings:
        raise Exception(f"Setting already exists: {name}")

    settings[name] = Setting(
        name, default, validator, channel, description, filter=filter
    )
