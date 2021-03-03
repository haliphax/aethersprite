"Roles self-service cog"

# stdlib
from typing import List
# 3rd party
from discord import Role
from discord.ext.commands import Cog, command, Context
# local
from aethersprite import log
from aethersprite.authz import channel_only
from aethersprite.common import get_mixed_roles
from aethersprite.filters import RoleFilter
from aethersprite.settings import register, settings

roles_filter = RoleFilter('roles.catalog')


class Roles(Cog, name='roles'):

    "Roles self-service commands (manage your own roles)"

    def __init__(self, bot):
        self.bot = bot

    def _validate(self, ctx: Context, roles: str) -> List[Role]:
        by_id = {}
        by_name = {}
        ids = settings['roles.catalog'].get(ctx, raw=True)

        for id in ids:
            role = [r for r in ctx.guild.roles if r.id == id][0]
            by_id[role.id] = role
            by_name[role.name.lower()] = role

        matches = get_mixed_roles(roles)
        to_add = []

        for m in matches:
            if m[0] != '':
                key = int(m[0])

                if key not in by_id:
                    return None

                to_add = by_id[key]
            else:
                key = m[1].lower()

                if key not in by_name:
                    return None

                to_add = by_name[key]

        return to_add

    @command(name='roles.add')
    async def add(self, ctx: Context, roles: str):
        """
        Add yourself to <roles>

        You may use mentions or plain text. Plain text entries should be separated by a comma.

        Mixed example: !roles.add @Role1 Role2, Role3 @Role4
        """

        valid = self._validate(ctx, roles)

        if valid is None:
            await ctx.send(':thumbsdown: Invalid role(s).')
            log.warn(f'{ctx.author} attempted invalid role(s) add: '
                        f'{roles}')

            return

        await ctx.author.add_roles(valid)
        await ctx.send(':thumbsup: Role(s) added.')
        log.info(f'{ctx.author} added roles: {valid}')


    @command(name='roles.remove')
    async def remove(self, ctx: Context, roles: str):
        """
        Remove yourself from <roles>

        You may use mentions or plain text. Plain text entries should be separated by a comma.

        Mixed example: !roles.remove @Role1 Role2, Role3 @Role4
        """

        valid = self._validate(ctx, roles)

        if valid is None:
            await ctx.send(':thumbsdown: Invalid role(s).')
            log.warn(f'{ctx.author} attempted invalid role(s) removal: '
                        f'{roles}')

            return

        await ctx.author.remove_roles(valid)
        await ctx.send(':thumbsup: Role(s) removed.')
        log.info(f'{ctx.author} removed roles: {valid}')

    @command(name='roles.list')
    async def list(self, ctx: Context):
        "List available self-service roles"

        roles = settings['roles.catalog'].get(ctx)
        msg = f":notebook: **Available roles**\n>>> - "

        if roles is None:
            msg += "`None`"
        else:
            msg += '\r\n- '.join(sorted(roles, key=lambda x: x.lower()))

        await ctx.send(msg)
        log.info(f'{ctx.author} viewed roles list')


def setup(bot):
    cog = Roles(bot)

    for c in cog.get_commands():
        c.add_check(channel_only)

    # settings
    register('roles.catalog', None, lambda x: True, False,
             'The roles members are allowed to add/remove themselves',
             filter=roles_filter)

    bot.add_cog(cog)


def teardown(bot):
    global settings

    del settings['roles.catalog']
