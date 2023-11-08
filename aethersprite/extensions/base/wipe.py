"""Wipe channel extension"""

# TODO track which channels are being actively wiped
# TODO resume wipes on startup; clear missing channels from db
# TODO remove wipe record on completion
# TODO command with channel param to cancel active wipe
# TODO command to list active wipes on server
# TODO channel retention policy setting -- automatically delete messages older \
#      than x days old on a schedule

# typing

# 3rd party
from discord.ext.commands import Bot, check, command, Context
from discord.channel import TextChannel
from discord.message import Message
from discord.raw_models import RawReactionActionEvent
from sqlitedict import SqliteDict

# api
from aethersprite import bot, data_folder, log
from aethersprite.authz import channel_only, require_admin
from aethersprite.emotes import CHECK_MARK, PROHIBITED


# database
wipes = SqliteDict(
    f"{data_folder}wipe.sqlite3",
    tablename="wipes",
    autocommit=True,
)


async def on_raw_reaction_add(payload: RawReactionActionEvent):
    """Handle on_reaction_add event."""

    assert bot.user
    assert payload.member
    assert payload.member.guild
    if (
        payload.user_id == bot.user.id
        or payload.guild_id not in wipes
        or wipes[payload.guild_id] != payload.message_id
    ):
        return

    channel: TextChannel = payload.member.guild.get_channel(
        payload.channel_id  # type: ignore
    )
    msg: Message = await channel.fetch_message(payload.message_id)
    perms = channel.permissions_for(payload.member)

    if not perms.manage_messages:
        await msg.remove_reaction(payload.emoji, payload.member)
        return

    if payload.emoji.name == PROHIBITED:
        log.info(f"{payload.member} canceled wipe in {channel}")
        await msg.delete()
        del wipes[payload.guild_id]
        return

    if payload.emoji.name != CHECK_MARK:
        await msg.remove_reaction(payload.emoji, payload.member)
        return

    log.info(f"{payload.member} began wipe in {channel}")
    del wipes[payload.guild_id]

    # stop after a million just to be safe?
    for _ in range(1_000_000):
        done = True
        log.info(f"Deleting up to 100 messages in {channel}")

        async for m in channel.history(limit=100):
            done = False
            await m.delete()

        if done:
            break

    log.info(f"{payload.member} finished wiping {channel}")


@command()
@check(channel_only)
@check(require_admin)
async def wipe(ctx: Context):
    """Delete all messages in a channel."""

    assert ctx.guild
    log.info(f"{ctx.author} requested wipe in {ctx.channel}")
    msg = await ctx.send("Are you sure?")
    await msg.add_reaction(PROHIBITED)
    await msg.add_reaction(CHECK_MARK)
    wipes[ctx.guild.id] = msg.id


async def setup(bot: Bot):
    bot.add_command(wipe)
    bot.add_listener(on_raw_reaction_add)
