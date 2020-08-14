"Safe contents commands"

# stdlib
from functools import partial
# 3rd party
from discord.ext import commands
from flask import abort, Blueprint, request
from sqlitedict import SqliteDict
# local
from .. import log
from ..authz import channel_only, require_admin, require_roles
from ..common import command, FakeContext
from ..settings import register, settings

#: Maximum number of items listed per Discord message to avoid rejection
MAX_ITEMS_PER_MESSAGE = 20

authz_safe = partial(require_roles, setting='safe.roles')
blueprint = Blueprint('safe', __name__, url_prefix='/safe')


def _get_database():
    "Helper function to get a database reference"

    return SqliteDict('safe.sqlite3', tablename='contents', autocommit=True)


class Safe(commands.Cog, name='safe'):

    "Safe contents commands"

    _safe = _get_database()
    #: Emoji to use when displaying lists
    _icons = {
        'Components': 'tools',
        'Potions': 'test_tube',
        'Spells': 'mage',
    }

    async def _get(self, ctx, kind):
        "Helper function for retrieving item lists"

        if settings['safe.key'].get(ctx) is None:
            await ctx.send(':thumbsdown: No UserScript key has been set.')

            return

        guild = str(ctx.guild.id)
        await ctx.send(f':{self._icons[kind]}: **{kind}**')
        msg = []
        items = []
        count = 0

        if guild in self._safe:
            items += self._safe[guild][kind]

        if not items:
            await ctx.send('> _None_')
        else:
            for i in items:
                msg.append(f'- {i}')
                count += 1

                if count % MAX_ITEMS_PER_MESSAGE == 0:
                    await ctx.send('>>> ' + '\n'.join(msg))
                    msg = []

        if len(msg):
            await ctx.send('>>> ' + '\n'.join(msg))

    @command()
    @commands.check(authz_safe)
    @commands.check(channel_only)
    async def potions(self, ctx):
        "Lists potions in the faction safe"

        await self._get(ctx, 'Potions')

    @command()
    @commands.check(authz_safe)
    @commands.check(channel_only)
    async def spells(self, ctx):
        "Lists spell gems in the faction safe"

        await self._get(ctx, 'Spells')

    @command()
    @commands.check(authz_safe)
    @commands.check(channel_only)
    async def components(self, ctx):
        "Lists components in the faction safe"

        await self._get(ctx, 'Components')


def _settings():
    "Helper function for registering settings"

    register('safe.key', None, lambda x: True, False,
             'The key used by the UserScript for reporting.')
    register('safe.roles', None, lambda x: True, False,
             'The server roles that are allowed to view safe contents. If set '
             'there are no restrictions. Separate multiple entries with '
             'commas.')

def setup(bot):
    "Discord bot setup"

    _settings()
    bot.add_cog(Safe(bot))


@blueprint.route('/post', methods=('POST',))
def http_safe():
    "Post safe contents from UserScript"

    from flask import current_app

    db = current_app.ext_safe_db
    data = request.get_json(force=True)

    for k in ('guild', 'items', 'key'):
        if k not in data:
            return abort(400)

    guild = data['guild']
    ctx = FakeContext(guild={'id': guild})
    key = settings['safe.key'].get(ctx)

    if key is None:
        return abort(401)

    if key != data['key']:
        return abort(403)

    # ignore spell/potion blind item reports
    for category in ('Potion', 'Spell',):
        items = data['items'][category]

        if len(items) == 0:
            continue

        if items[0] == '0':
            try:
                data['items'][category] = db[guild][category]
            except KeyError:
                data['items'][category] = []

    db[guild] = {
        'Potions': data['items']['Potion'],
        'Spells': data['items']['Spell'],
        'Components': data['items']['Component'],
    }

    return '', 200


def setup_webapp(app):
    "Web application setup"

    _settings()
    db = _get_database()
    setattr(app, 'ext_safe_db', db)
    app.register_blueprint(blueprint)
