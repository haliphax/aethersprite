"Roles self-service cog"

# stdlib
import asyncio as aio
from datetime import datetime, timedelta
from typing import Optional
# 3rd party
from discord import Color, Embed, Guild, Member, Message, TextChannel
from discord.errors import NotFound
from discord.ext.commands import Bot, check, command, Context
from discord.raw_models import RawReactionActionEvent
from sqlitedict import SqliteDict
# local
from aethersprite import data_folder, log
from aethersprite.authz import channel_only, require_admin
from aethersprite.common import FakeContext, seconds_to_str
from aethersprite.filters import RoleFilter, SettingFilter
from aethersprite.settings import register, settings

bot: Bot = None
loop = aio.get_event_loop()
# constants
DIGIT_SUFFIX = '\ufe0f\u20e3'
# filters
roles_filter = RoleFilter('roles.catalog')
# database
postdb_file = f'{data_folder}roles.sqlite3'
posts = SqliteDict(postdb_file, tablename='selfserv_posts', autocommit=True)
directories = SqliteDict(postdb_file, tablename='catalog', autocommit=True)

def _update_filter(self, ctx: Context, value: str) -> None:
    val = super(RoleFilter, self).in_(ctx, value)
    directory = directories[ctx.guild.id] \
        if ctx.guild.id in directories else None

    if directory is None:
        return val

    chan: TextChannel = ctx.guild.get_channel(directory['channel'])

    if chan is None:
        return val

    async def update():
        msg = await chan.fetch_message(directory['message'])

        if msg is None:
            return

        await _get_message(ctx, msg)

    aio.get_event_loop().run_until_complete(update())

    return val


# monkey patch :(
roles_filter.in_ = _update_filter


async def _get_message(ctx: Context, msg: Optional[Message] = None,
        expiry: Optional[str] = None):
    roles = settings['roles.catalog'].get(ctx)[:10]
    embed = Embed(title=f':billed_cap: Available roles',
                  description='Use post reactions to manage role membership',
                  color=Color.purple())

    if expiry is not None:
        embed.set_footer(text=f'This post will be deleted in {expiry}.')

    count = 0

    for role in sorted(roles, key=lambda x: x.lower()):
        embed.add_field(name=f'{count}{DIGIT_SUFFIX} {role}', value='\u200b')
        count += 1

    if msg is None:
        msg: Message = await ctx.send(embed=embed)
    else:
        await msg.edit(embed=embed)
        await msg.reactions.clear()

    for i in range(0, count):
        await msg.add_reaction(f'{i}{DIGIT_SUFFIX}')

    return msg


@command()
@check(channel_only)
async def roles(ctx: Context):
    "Manage your membership in available roles"

    expiry_raw = settings['roles.postexpiry'].get(ctx)
    expiry = seconds_to_str(expiry_raw)
    roles = settings['roles.catalog'].get(ctx)

    if roles is None or len(roles) == 0:
        await ctx.send(':person_shrugging: There are no available '
                       'self-service roles.')
        log.warn(f'{ctx.author} invoked roles self-service, but no roles are '
                 'available')

        return

    msg = await _get_message(ctx, expiry=expiry)
    posts[msg.id] = {'guild': ctx.guild.id,
                     'channel': ctx.channel.id,
                     'expiry': datetime.utcnow()
                     + timedelta(seconds=expiry_raw)}

    log.info(f'{ctx.author} invoked roles self-service')
    loop.call_later(expiry_raw, _delete, msg.id)
    await ctx.message.delete()


@command(name='roles.catalog')
@check(channel_only)
@check(require_admin)
async def catalog(ctx: Context):
    "Create a permanent roles catalog post in the current channel."

    roles = settings['roles.catalog'].get(ctx)

    if roles is None or len(roles) == 0:
        await ctx.send(':person_shrugging: There are no available '
                       'self-service roles.')
        log.warn(f'{ctx.author} attempted to post roles catalog, but no roles '
                 'are available')

        return

    guild_id = str(ctx.guild.id)

    if guild_id in directories:
        existing = directories[guild_id]
        chan: TextChannel = ctx.guild.get_channel(existing['channel'])

        if chan is not None:
            msg = await chan.fetch_message(existing['message'])

            if msg is not None:
                await msg.delete()

    msg = await _get_message(ctx)
    directories[guild_id] = {'message': msg.id,
                             'channel': ctx.channel.id}

    log.info(f'{ctx.author} posted roles catalog to {ctx.channel}')
    await ctx.message.delete()


async def on_raw_reaction_add(payload: RawReactionActionEvent):
    "Handle on_reaction_add event."

    if payload.user_id == bot.user.id:
        return

    directory = directories[payload.guild_id] \
        if payload.guild_id in directories else None

    if payload.message_id not in posts and (
            directory is None or payload.message_id != directory['message']):
        return

    guild: Guild = bot.get_guild(payload.guild_id)
    channel: TextChannel = guild.get_channel(payload.channel_id)
    message: Message = await channel.fetch_message(payload.message_id)
    member: Member = guild.get_member(payload.user_id)
    split = str(payload.emoji).split('\ufe0f')

    if len(split) != 2:
        await message.remove_reaction(payload.emoji, member)

        return

    fake_ctx = FakeContext(guild=guild)
    setting = settings['roles.catalog'].get(fake_ctx, raw=True)
    roles = sorted([r for r in guild.roles if r.id in setting],
                   key=lambda x: x.name.lower())
    which = int(split[0])

    if which < 0 or which > len(roles):
        await message.remove_reaction(payload.emoji, member)

        return

    role = roles[which]
    await member.add_roles(role)
    log.info(f'{member} added role {role}')


async def on_raw_reaction_remove(payload: RawReactionActionEvent):
    "Handle on_reaction_remove event."

    if payload.user_id == bot.user.id:
        return

    directory = directories[payload.guild_id] \
        if payload.guild_id in directories else None

    if payload.message_id not in posts and (
            directory is None or payload.message_id != directory['message']):
        return

    split = str(payload.emoji).split('\ufe0f')

    if len(split) != 2:
        return

    guild: Guild = bot.get_guild(payload.guild_id)
    member: Member = guild.get_member(payload.user_id)
    fake_ctx = FakeContext(guild=guild)
    setting = settings['roles.catalog'].get(fake_ctx, raw=True)
    roles = sorted([r for r in guild.roles if r.id in setting],
                   key=lambda x: x.name.lower())
    which = int(split[0])

    if which < 0 or which > len(roles):
        return

    role = roles[which]
    await member.remove_roles(role)
    log.info(f'{member} removed role {role}')


async def on_ready():
    "Clear expired/missing roles posts on startup."

    # clean up missing directories
    for guild_id, directory in directories.items():
        try:
            guild: Guild = bot.get_guild(int(guild_id))
            chan: TextChannel = guild.get_channel(directory['channel'])
            msg = await chan.fetch_message(directory['message'])
        except NotFound:
            log.warn(f'Deleted missing directory post for {guild_id}')
            del directories[guild_id]

    # clean up expired posts
    now = datetime.utcnow()

    for id, msg in posts.items():
        if msg['expiry'] <= now:
            _delete(id)
        else:
            expiry: datetime = msg['expiry']
            diff = (expiry - now).total_seconds()
            loop.call_later(diff, _delete, id)
            log.debug(f'Scheduled deletion of self-service post {id}')


def _delete(id: int):
    if id not in posts:
        return

    post = posts[id]
    guild: Guild = bot.get_guild(post['guild'])
    channel: TextChannel = guild.get_channel(post['channel'])

    async def f():
        try:
            msg: Message = await channel.fetch_message(id)
            await msg.delete()
        except NotFound:
            pass

        del posts[id]

    aio.ensure_future(f())
    log.info(f'Deleted roles self-service post {id}')


def setup(bot_: Bot):
    global bot

    bot = bot_

    # settings
    register('roles.catalog', None, lambda x: True, False,
             'The roles members are allowed to add/remove themselves',
             filter=roles_filter)
    register('roles.postexpiry', 60, lambda x: True, False,
             'The length of time (in seconds) to keep self-service posts')

    # events
    bot.add_listener(on_raw_reaction_add)
    bot.add_listener(on_raw_reaction_remove)
    bot.add_listener(on_ready)

    bot.add_command(roles)
    bot.add_command(catalog)


def teardown(bot):
    global settings

    del settings['roles.catalog']
