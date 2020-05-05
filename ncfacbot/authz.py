"Authorization module"

from discord import DMChannel


async def channel_only(ctx):
    "Check for bot commands that should only operate in a channel"

    if type(ctx.channel) is DMChannel:
        await ctx.send('This command must be used in a channel.')

        return False

    return True


async def require_admin(ctx):
    "Check for requiring admin/mod privileges to execute a command."

    perms = ctx.author.permissions_in(ctx.channel)

    if perms.administrator or perms.manage_channels or perms.manage_guild \
            or ctx.bot.owner_id == ctx.author.id:
        return True

    return False


async def require_roles(ctx, setting):
    """
    Check for requiring particular roles (loaded from the given setting) to
    execute a command. For more than one setting (if ``setting`` is a
    list/tuple), the aggregate list will be used. Membership in at least one of
    the roles pulled from the settings is required to pass the filter.

    Example, if your setting with role(s) is ``setting.name``:

    .. code-block:: python

        from functools import partial
        from discord.ext import commands
        from ncfacbot.authz import require_roles
        from ncfacbot.common import command

        authz = partial(require_roles, setting='setting.name')

        @command()
        @commands.check(authz)
        async def my_command(ctx):
            await ctx.send('You are authorized. Congratulations!')

    :param setting: The name of the setting to pull the roles from
    :type setting: str or list or tuple
    """

    # import at call-time to avoid cyclic reference
    from .settings import settings

    perms = ctx.author.permissions_in(ctx.channel)
    pass_ = False

    if perms.administrator or perms.manage_channels or perms.manage_guild \
            or ctx.bot.owner_id == ctx.author.id:
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

        return False

    return True
