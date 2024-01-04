# 3rd party
from discord.ext.commands import Context

# local
from ..common import get_id_for_role, get_mixed_roles, get_role_for_id
from .setting_filter import SettingFilter


class RoleFilter(SettingFilter):

    """Filter used for converting role names to IDs and back"""

    multiple: bool = True
    """True to allow multiple values"""

    def __init__(self, setting: str, multiple: bool = True):
        super().__init__(setting)
        self.multiple = multiple

    def in_(self, ctx: Context, value: str | None) -> list[int] | None:
        """
        Filter setting input.

        Args:
            ctx: The current context
            value: The incoming value

        Returns:
            The raw setting value (a list of role IDs)
        """

        if not value:
            return

        roles = get_mixed_roles(value)
        ids = []

        for r in roles:
            id = None

            if r[0] == "":
                id = get_id_for_role(ctx.guild, r[1])
            else:
                # convert mentions, if any
                id = int(r[0])

            if id is None:
                raise ValueError(r)

            ids.append(id)

            if not self.multiple:
                break

        return ids

    def out(
        self,
        ctx: Context,
        value: list[int] | None,
    ) -> list[str | None] | str | None:
        """
        Filter setting output.

        Args:
            ctx: The current context
            value: The raw setting value: a list of role IDs

        Returns:
            The filtered setting value (a list of role names)
        """

        if value is None:
            return

        roles = [get_role_for_id(ctx.guild, v) for v in value]

        if self.multiple:
            return roles

        if len(roles) > 0:
            return roles[0]

        return None
