"""Setting filter base class"""

# typing
from typing import Any

# 3rd party
from discord.ext.commands import Context


class SettingFilter(object):
    """A class with methods for filtering a setting's input and output"""

    setting: str
    """The name of the setting to filter"""

    def __init__(self, setting: str):
        self.setting = setting

    def in_(self, ctx: Context, value: str | None) -> Any | None:
        """
        Must override; input filter method.

        Args:
            ctx: The current context
            value: The incoming value

        Returns:
            The raw setting value(s), for reference
        """

        raise NotImplementedError()

    def out(self, ctx: Context, value: Any | None) -> Any | None:
        """
        Must override; output filter method.

        Args:
            ctx: The current context
            value: The raw setting value

        Returns:
            The filtered setting value(s)
        """

        raise NotImplementedError()
