"""Roles self-service cog"""

# stdlib
import asyncio as aio
from datetime import datetime, timedelta

# 3rd party
from discord import Color, Embed, Message
from discord.errors import NotFound
from discord.ext.commands import Bot, check, command, Context
from discord.raw_models import RawReactionActionEvent
from sqlitedict import SqliteDict

# local
from aethersprite import bot, data_folder, log
from aethersprite.authz import channel_only, require_admin
from aethersprite.common import FakeContext, seconds_to_str
from aethersprite.filters import RoleFilter
from aethersprite.settings import register, settings

loop = aio.get_event_loop()
# constants
DIGIT_SUFFIX = "\ufe0f\u20e3"
# database
postdb_file = f"{data_folder}roles.sqlite3"
posts = SqliteDict(postdb_file, tablename="selfserv_posts", autocommit=True)
directories = SqliteDict(postdb_file, tablename="catalog", autocommit=True)


class DirectoryUpdateFilter(RoleFilter):

    """Automatically update directory post when roles.catalog is updated"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def in_(self, ctx: Context, value: str) -> list[int] | None:
        """Filter input."""

        assert ctx.guild
        val = super().in_(ctx, value)
        directory = (
            directories[ctx.guild.id] if ctx.guild.id in directories else None
        )

        if directory is None:
            return val

        chan = ctx.guild.get_channel(directory["channel"])

        if chan is None:
            return val

        async def update():
            try:
                msg = await chan.fetch_message(  # type: ignore
                    directory["message"],
                )
                await _get_message(ctx, msg)
            except NotFound:
                pass

        aio.ensure_future(update())

        return val


roles_filter = DirectoryUpdateFilter("roles.catalog")


async def _get_message(
    ctx: Context,
    msg: Message | None = None,
    expiry: str | None = None,
):
    roles_: list[str] = settings["roles.catalog"].get(ctx)[:10]  # type: ignore
    embed = Embed(
        title=":billed_cap: Available roles",
        description="Use post reactions to manage role membership",
        color=Color.purple(),
    )

    if expiry is not None:
        embed.set_footer(text=f"This post will be deleted in {expiry}.")

    count = 0

    for role in sorted(roles_, key=lambda x: x.lower()):
        embed.add_field(name=f"{count}{DIGIT_SUFFIX} {role}", value="\u200b")
        count += 1

    if msg is None:
        msg = await ctx.send(embed=embed)
    else:
        await msg.edit(embed=embed)
        await msg.clear_reactions()

    for i in range(0, count):
        await msg.add_reaction(f"{i}{DIGIT_SUFFIX}")

    return msg


@command()
@check(channel_only)
async def roles(ctx: Context):
    """Manage your membership in available roles"""

    assert ctx.guild

    expiry_raw: int = settings["roles.postexpiry"].get(ctx)  # type: ignore
    expiry = seconds_to_str(expiry_raw)
    roles_ = settings["roles.catalog"].get(ctx)

    if roles_ is None or len(roles_) == 0:
        await ctx.send(
            ":person_shrugging: There are no available self-service roles."
        )
        log.warn(
            f"{ctx.author} invoked roles self-service, but no roles are available"
        )

        return

    msg = await _get_message(ctx, expiry=expiry)
    posts[msg.id] = {
        "guild": ctx.guild.id,
        "channel": ctx.channel.id,
        "expiry": datetime.utcnow() + timedelta(seconds=expiry_raw),
    }

    log.info(f"{ctx.author} invoked roles self-service")
    loop.call_later(expiry_raw, _delete, msg.id)
    await ctx.message.delete()


@command()
@check(channel_only)
@check(require_admin)
async def catalog(ctx: Context):
    """Create a permanent roles catalog post in the current channel."""

    assert ctx.guild

    roles_ = settings["roles.catalog"].get(ctx)

    if roles_ is None or len(roles_) == 0:
        await ctx.send(
            ":person_shrugging: There are no available " "self-service roles."
        )
        log.warn(
            f"{ctx.author} attempted to post roles catalog, but no roles "
            "are available"
        )

        return

    guild_id = str(ctx.guild.id)

    if guild_id in directories:
        existing = directories[guild_id]
        chan = ctx.guild.get_channel(existing["channel"])

        if chan is not None:
            try:
                msg = await chan.fetch_message(  # type: ignore
                    existing["message"],
                )
                await msg.delete()
            except NotFound:
                pass

    msg = await _get_message(ctx)
    directories[guild_id] = {"message": msg.id, "channel": ctx.channel.id}

    log.info(f"{ctx.author} posted roles catalog to {ctx.channel}")
    await ctx.message.delete()


async def on_raw_reaction_add(payload: RawReactionActionEvent):
    """Handle on_reaction_add event."""

    assert bot.user
    assert payload.guild_id

    if payload.user_id == bot.user.id:
        return

    directory = (
        directories[payload.guild_id]
        if payload.guild_id in directories
        else None
    )

    if payload.message_id not in posts and (
        directory is None or payload.message_id != directory["message"]
    ):
        return

    guild = bot.get_guild(payload.guild_id)
    assert guild
    channel = guild.get_channel(payload.channel_id)
    assert channel
    message = await channel.fetch_message(  # type: ignore
        payload.message_id,
    )
    member = guild.get_member(payload.user_id)
    assert member
    split = str(payload.emoji).split("\ufe0f")

    if len(split) != 2:
        await message.remove_reaction(payload.emoji, member)

        return

    fake_ctx = FakeContext(guild=guild)
    setting: list[int] = settings["roles.catalog"].get(
        fake_ctx, raw=True  # type: ignore
    )
    roles_ = sorted(
        [r for r in guild.roles if r.id in setting],
        key=lambda x: x.name.lower(),
    )
    which = int(split[0])

    if which < 0 or which > len(roles_):
        await message.remove_reaction(payload.emoji, member)

        return

    role = roles_[which]
    await member.add_roles(role)
    log.info(f"{member} added role {role}")


async def on_raw_reaction_remove(payload: RawReactionActionEvent):
    """Handle on_reaction_remove event."""

    assert bot.user
    assert payload.guild_id

    if payload.user_id == bot.user.id:
        return

    directory = (
        directories[payload.guild_id]
        if payload.guild_id in directories
        else None
    )

    if payload.message_id not in posts and (
        directory is None or payload.message_id != directory["message"]
    ):
        return

    split = str(payload.emoji).split("\ufe0f")

    if len(split) != 2:
        return

    guild = bot.get_guild(payload.guild_id)
    assert guild
    member = guild.get_member(payload.user_id)
    assert member
    fake_ctx = FakeContext(guild=guild)
    setting: list[int] = settings["roles.catalog"].get(
        fake_ctx, raw=True  # type: ignore
    )
    roles_ = sorted(
        [r for r in guild.roles if r.id in setting],
        key=lambda x: x.name.lower(),
    )
    which = int(split[0])

    if which < 0 or which > len(roles_):
        return

    role = roles_[which]
    await member.remove_roles(role)
    log.info(f"{member} removed role {role}")


async def on_ready():
    """Clear expired/missing roles posts on startup."""

    # clean up missing directories
    for guild_id, directory in directories.items():
        try:
            guild = bot.get_guild(int(guild_id))
            assert guild
            chan = guild.get_channel(directory["channel"])
            assert chan
            msg = await chan.fetch_message(  # type: ignore
                directory["message"],
            )
        except NotFound:
            log.warn(f"Deleted missing directory post for {guild_id}")
            del directories[guild_id]

    # clean up expired posts
    now = datetime.utcnow()

    for id, msg in posts.items():
        if msg["expiry"] <= now:
            _delete(id)
        else:
            expiry: datetime = msg["expiry"]
            diff = (expiry - now).total_seconds()
            loop.call_later(diff, _delete, id)
            log.debug(f"Scheduled deletion of self-service post {id}")


def _delete(id: int):
    if id not in posts:
        return

    post = posts[id]
    guild = bot.get_guild(post["guild"])
    assert guild
    channel = guild.get_channel(post["channel"])

    async def f():
        try:
            msg: Message = await channel.fetch_message(  # type: ignore
                id,
            )
            await msg.delete()
        except NotFound:
            pass

        del posts[id]

    aio.ensure_future(f())
    log.info(f"Deleted roles self-service post {id}")


async def setup(bot: Bot):
    # settings
    register(
        "roles.catalog",
        None,
        lambda x: True,
        False,
        "The roles members are allowed to add/remove themselves",
        filter=roles_filter,
    )
    register(
        "roles.postexpiry",
        60,
        lambda x: True,
        False,
        "The length of time (in seconds) to keep self-service posts",
    )

    # events
    bot.add_listener(on_raw_reaction_add)
    bot.add_listener(on_raw_reaction_remove)
    bot.add_listener(on_ready)

    bot.add_command(catalog)
    bot.add_command(roles)


async def teardown(bot):
    global settings

    del settings["roles.catalog"]
