"Authorization module"

# stdlib
from os import environ
from typing import Sequence
# 3rd party
from discord import DMChannel, Member, Role
from discord.ext.commands import Context
# local
from . import config, log
from .common import POLICE_OFFICER
from .settings import settings

owner = config['bot'].get('owner', environ.get('NCFACBOT_OWNER', None))
_help = config['bot']['help_command']


async def channel_only(ctx):
    "Check for bot commands that should only operate in a channel"

    if isinstance(ctx.channel, DMChannel):
        await ctx.send('This command must be used in a channel.')

        return False

    return True


def is_in_any_role(user: Member, roles: Sequence[Role]) -> bool:
    """
    Whether or not a member is in any of the given roles.

    :param user: The user in question
    :param roles: The roles to check for membership
    """

    if len(roles) > 0 and len([r for r in user.roles if r in roles]) > 0:
        return True

    return False

async def react_if_not_help(ctx: Context):
    """
    If the command was not invoked as an alias of the help command, react with
    the police officer emoji.

    :param ctx: The current context
    """

    cog = ctx.bot.get_cog('alias')

    if cog is None:
        log.warn('alias cog not loaded')

        return


    aliases = cog.get_aliases(ctx, _help)
    help_aliases = [_help] + aliases

    # only react if they invoked the command directly (i.e. not via !help)
    if ctx.invoked_with not in help_aliases:
        await ctx.message.add_reaction(POLICE_OFFICER)
        log.warn(f'{ctx.author} attempted to access unauthorized command '
                 f'{ctx.command}')

    return

async def require_admin(ctx):
    "Check for requiring admin/mod privileges to execute a command."

    perms = ctx.author.permissions_in(ctx.channel)

    if perms.administrator or perms.manage_channels or perms.manage_guild \
            or owner == str(ctx.author):
        return True

    cog = ctx.bot.get_cog('alias')

    if cog is None:
        return False

    aliases = cog.get_aliases(ctx, _help)
    help_aliases = [_help] + aliases

    # only react if they invoked the command directly (i.e. not via !help)
    if ctx.invoked_with not in help_aliases:
        await ctx.message.add_reaction(POLICE_OFFICER)
        log.warn(f'{ctx.author} attempted to access admin command '
                 f'{ctx.command}')

    return False


async def require_roles(ctx: Context, roles: Sequence[Role]) -> bool:
    """
    Check for requiring particular roles to execute a command. Membership in at
    least one of the roles is requied to pass the filter.

    :param ctx: The current context
    :param roles: The roles to authorize
    """

    if is_in_any_role(ctx.author, roles):
        return True

    await react_if_not_help(ctx)

    return False

async def require_roles_from_setting(ctx: Context, setting: str,
                                     open_by_default=True) -> bool:
    """
    Check for requiring particular roles (loaded from the given setting) to
    execute a command. For more than one setting (if ``setting`` is a
    list/tuple), the aggregate list will be used. Membership in at least one of
    the roles pulled from the settings is required to pass the filter.

    If this check is used and the setting is empty or nonexistent, the default
    behavior is to allow anyone and everyone to use the command. If you would
    like for it to default to "closed" behavior, set the ``open_by_default``
    argument to ``False``.

    Example, if your setting with role(s) is ``setting.name``:

    .. code-block:: python

        from functools import partial
        from discord.ext.commands import check, command
        from aethersprite.authz require_roles, import require_roles_from_setting
        from my_super_secret_special_code import get_roles

        authz = partial(require_roles, get_roles())
        authz_setting = partial(require_roles_from_setting, setting='setting.name')

        @command()
        @check(authz)
        async def my_command(ctx):
            await ctx.send('You are authorized. Congratulations!')

        @command()
        @check(authz_setting)
        async def my_other_command(ctx):
            # to set via bot command: !set setting.name SomeRoleName, SomeOtherRole
            await ctx.send('You are a member of one of the authorized roles. '
                           'Congratulations!')

    :param setting: The name of the setting to pull the roles from
    :type setting: str or list or tuple
    """

    perms = ctx.author.permissions_in(ctx.channel)

    if perms.administrator or perms.manage_channels or perms.manage_guild \
            or owner == str(ctx.author):
        # Superusers get a pass
        return True

    roles_id = [int(r) for r in settings[setting].get(ctx, raw=True)]

    if roles_id is None:
        # no roles set, use default
        return open_by_default

    for r in ctx.author.roles:
        if r.id in roles_id:
            return True

    await react_if_not_help(ctx)

    return False
