"Authorization module"

# stdlib
from os import environ
# 3rd party
from discord import DMChannel
# local
from . import config, log
from .common import POLICE_OFFICER

owner = config['bot'].get('owner', environ.get('NCFACBOT_OWNER', None))
_help = config['bot']['help_command']


async def channel_only(ctx):
    "Check for bot commands that should only operate in a channel"

    if isinstance(ctx.channel, DMChannel):
        await ctx.send('This command must be used in a channel.')

        return False

    return True


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


async def require_roles(ctx, setting, open_by_default=True):
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
        from aethersprite.authz import require_roles

        authz = partial(require_roles, setting='setting.name')

        @command()
        @check(authz)
        async def my_command(ctx):
            await ctx.send('You are authorized. Congratulations!')

        # to set via bot command: !set setting.name SomeRoleName, SomeOtherRole

    :param setting: The name of the setting to pull the roles from
    :type setting: str or list or tuple
    """

    # import at call-time to avoid cyclic reference
    from .settings import settings

    perms = ctx.author.permissions_in(ctx.channel)

    if perms.administrator or perms.manage_channels or perms.manage_guild \
            or owner == str(ctx.author):
        # Superusers get a pass
        return True

    values = None

    if isinstance(setting, str):
        values = settings[setting].get(ctx)
    elif isinstance(setting, (list, tuple)):
        names = []

        for s in setting:
            val = settings[s].get(ctx)

            if val is not None:
                names.append(val)

        values = ','.join(names)
    else:
        raise ValueError('setting must be str, list, or tuple')

    if values is None:
        # no roles set, use default
        return open_by_default

    roles = [s.strip().lower() for s in values.split(',')] \
            if len(values) else tuple()

    if len(roles) > 0 and len([r for r in ctx.author.roles
                               if r.name.lower() in roles]) > 0:
        return True

    cog = ctx.bot.get_cog('alias')

    if cog is None:
        log.warn('alias cog not loaded')

        return False

    aliases = cog.get_aliases(ctx, _help)
    help_aliases = [_help] + aliases

    # only react if they invoked the command directly (i.e. not via !help)
    if ctx.invoked_with not in help_aliases:
        await ctx.message.add_reaction(POLICE_OFFICER)
        log.warn(f'{ctx.author} attempted to access unauthorized command '
                 f'{ctx.command}')

    return False
