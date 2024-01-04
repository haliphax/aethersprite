"""Settings commands; store, view, and manipulate settings"""

# 3rd party
from discord.channel import TextChannel
from discord.ext.commands import Bot, Cog, command, Context
from functools import partial

# local
from aethersprite import log
from aethersprite.authz import channel_only, require_roles_from_setting
from aethersprite.filters import RoleFilter
from aethersprite.settings import register, settings

# messages
MSG_NO_SETTING = ":person_shrugging: No such setting exists."

authz = partial(
    require_roles_from_setting,
    setting="settings.adminroles",
    open_by_default=False,
)
"""Authorization decorator"""


class Settings(Cog):

    """
    Settings commands

    View settings, change settings, reset settings, and view settings descriptions.
    """

    def __init__(self, bot):
        self.bot = bot

    @command(name="get.all")
    async def get_all(self, ctx: Context):
        """View a list of all settings"""

        settings_str = "**, **".join(sorted(settings.keys()))
        await ctx.send(f":gear: All settings: **{settings_str}**")
        log.info(f"{ctx.author} viewed all settings")

    @command()
    async def get(
        self,
        ctx: Context,
        name: str,
        channel: TextChannel | None = None,
    ):
        """
        View a setting's value

        Use the 'channel' parameter to specify a channel other than the current one.

        Examples:
            !get key
            !get key #lobby
        """

        if not channel:
            channel = ctx.channel  # type: ignore
            assert channel

        val = settings[name].get(ctx, channel=channel.id)
        default = settings[name].default
        await ctx.send(
            f":gear: `{name}`\n"
            f">>> Value: `{repr(val)}`\n"
            f"Default: `{repr(default)}`"
        )
        log.info(f"{ctx.author} viewed setting {name} in {channel}")

    @command()
    async def set(
        self,
        ctx: Context,
        name: str,
        value: str,
        channel: TextChannel | None = None,
    ):
        """
        Change/view a setting's value

        Note that channel-dependent settings must be set and viewed in relevant channels.

        You may provide a channel other than the current one.

        When used on a boolean (True/False) setting, ANY VALUE will toggle the setting to the opposite of its default value.

        Examples:
            !set key value
            !set key value #lobby
        """

        if not channel:
            channel = ctx.channel  # type: ignore
            assert channel

        if name not in settings:
            await ctx.send(MSG_NO_SETTING)
            log.warn(
                f"{ctx.author} attempted to set nonexistent setting: "
                f"{name} in {channel}"
            )

            return

        if settings[name].set(ctx, value, channel=channel.id):
            await ctx.send(":thumbsup: Value updated.")
            log.info(
                f"{ctx.author} updated setting {name}: {value} in {channel}"
            )
        else:
            await ctx.send(":thumbsdown: Error updating value.")
            log.warn(
                f"{ctx.author} failed to update setting {name}: {value} "
                f"in {channel}"
            )

    @command()
    async def clear(
        self,
        ctx: Context,
        name: str,
        channel: TextChannel | None = None,
    ):
        """
        Reset setting <name> to its default value

        You may provide a channel other than the current one.

        Examples:
            !clear key
            !clear key #lobby
        """

        if not channel:
            channel = ctx.channel  # type: ignore
            assert channel

        if name not in settings:
            log.warn(
                f"{ctx.author} attempted to clear nonexistent setting: "
                f"{name} in {channel}"
            )
            await ctx.send(MSG_NO_SETTING)

            return

        settings[name].set(ctx, None, raw=True, channel=channel.id)
        await ctx.send(":negative_squared_cross_mark: Setting cleared.")
        log.info(f"{ctx.author} cleared setting {name} in {channel}")

    @command()
    async def desc(self, ctx: Context, name: str):
        """View description of setting <name>"""

        if name not in settings:
            await ctx.send(MSG_NO_SETTING)
            log.warn(
                f"{ctx.author} attempted to view description of "
                f"nonexistent setting {name}"
            )

            return

        setting = settings[name]

        if setting.description is None:
            await ctx.send(":person_shrugging: No description set.")
        else:
            await ctx.send(
                f":book: `{setting.name}` "
                f"_(Channel: **{str(setting.channel)}**)_\n"
                f"> {setting.description}"
            )

        log.info(f"{ctx.author} viewed description of setting {name}")


role_filter = RoleFilter("settings.adminroles")


async def setup(_bot: Bot):
    global bot

    bot = _bot

    # settings
    register(
        "settings.adminroles",
        None,
        lambda x: True,
        False,
        "The server roles that are allowed to administer settings. "
        "Separate multiple values with commas. Administrators and "
        "moderators have de facto access to all commands.",
        filter=role_filter,
    )
    cog = Settings(bot)

    for c in cog.get_commands():
        c.add_check(authz)
        c.add_check(channel_only)

    await bot.add_cog(cog)
