"""Boolean setting filter"""

# 3rd party
from discord.ext.commands import Context

# api
from aethersprite.settings import settings

# local
from .setting_filter import SettingFilter


class BooleanFilter(SettingFilter):
    """Filter used for converting strings to boolean values"""

    def __init__(self, setting: str):
        super().__init__(setting)

    def in_(self, ctx: Context, value: str | None) -> bool | None:
        """
        Filter setting input.

        Args:
            ctx: The current context
            value: The incoming value

        Returns:
            The raw setting value (a boolean)
        """

        if value is None:
            return

        # boolean settings are just toggles; if they're set, they are the
        # opposite of the default
        return not settings[self.setting].default

    def out(
        self,
        ctx: Context,
        value: bool | None,
    ) -> bool | None:
        """
        Filter setting output.

        Args:
            ctx: The current context
            value: The raw setting value (a boolean)

        Returns:
            The raw setting value
        """

        return value
