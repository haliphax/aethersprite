"Poll cog"

# stdlib
import re
from functools import partial
# 3rd party
from discord import Message, Reaction, User
from discord.ext.commands import check, command, Context
from discord.ext.commands.bot import Bot
from sqlitedict import SqliteDict
# local
from aethersprite import log, data_folder
from aethersprite.authz import channel_only, require_roles_from_setting
from aethersprite.common import THUMBS_DOWN
from aethersprite.filters import RoleFilter
from aethersprite.settings import register, settings

# constants
DIGIT_SUFFIX = '\ufe0f\u20e3'
SOLID_BLOCK = '\u2588'
SHADE_BLOCK = '\u2591'

bot: Bot = None
# database
polls = SqliteDict(f'{data_folder}poll.sqlite3', tablename='polls',
                   autocommit=True)
# filters
create_filter = RoleFilter('poll.createroles')
vote_filter = RoleFilter('poll.voteroles')
# authz checks
authz_create = partial(require_roles_from_setting, setting='poll.createroles')
authz_vote = partial(require_roles_from_setting, setting='poll.voteroles')


@command()
@check(channel_only)
async def poll(ctx: Context, *, options: str):
    """
    Create a poll

    To create a poll, options must be provided. Separate options with commas. You may provide a prompt if you wish by encasing the first argument to the command in brackets.

    To delete a poll, use both the Delete and Confirm reactions. Only a moderator, administrator, or the creator of the poll may delete it.

    Examples:
        !poll The dress is green, The dress is gold
        !poll [Do you see what I see?] Yes, No
    """

    match = re.match(r'^(?:\[([^\]]+)\]\s*)?(.+)$', options)

    if match is None:
        await ctx.message.add_reaction(THUMBS_DOWN)
        log.warn(f'{ctx.author} Provided invalid arguments: {options}')

        return

    prompt, qstr = match.groups()
    count = 1
    opts = {}

    for s in qstr.split(','):
        emoji = f'{count}{DIGIT_SUFFIX}'
        opt = s.strip()
        opts[emoji] = {'text': opt, 'count': 0}
        count += 1

    poll = {'prompt': prompt, 'options': opts}
    msg: Message = await ctx.send(_get_text(poll))

    for emoji in opts.keys():
        await msg.add_reaction(emoji)

    polls[msg.id] = poll
    log.info(f'{ctx.author} created poll: {poll!r}')


def _get_text(poll):
    total = sum([int(o['count']) for _, o in poll['options'].items()])
    txt = [f':grey_question: **__{poll["prompt"] or "Poll"}__**']

    for key, opt in poll['options'].items():
        count = int(opt['count'])
        rawpct = round(0 if (total == 0 or count == 0)
                       else (count / total) * 100, 2)
        pct = 0 if (total == 0 or count == 0) else round((count / total) * 10)
        left = 10 - pct
        bar = f'{SOLID_BLOCK * pct}{SHADE_BLOCK * left}'
        txt.append(f'> {key} {bar} **{opt["text"]}** :: {opt["count"]} '
                   f'({rawpct}%)')

    txt.append('\nVote using reactions.')

    return '\n'.join(txt)


async def _update_poll(reaction: Reaction, adjustment: int):
    poll = polls[reaction.message.id]
    opts = poll['options']
    opt = opts[reaction.emoji]
    opt['count'] += adjustment
    opts[reaction.emoji] = opt
    poll['options'] = opts
    polls[reaction.message.id] = poll
    await reaction.message.edit(content=_get_text(poll))


async def on_reaction_add(reaction: Reaction, user: User):
    "Handle on_reaction_add event."

    if user.id == bot.user.id or reaction.message.id not in polls:
        return

    poll = polls[reaction.message.id]
    opts = poll['options']

    if reaction.emoji not in opts:
        return

    await _update_poll(reaction, 1)
    log.info(f'{user} voted for {reaction.emoji} - {poll["prompt"]}')


async def on_reaction_remove(reaction: Reaction, user: User):
    "Handle on_reaction_remove event."

    if reaction.message.id not in polls:
        return

    poll = polls[reaction.message.id]
    opts = poll['options']

    if reaction.emoji not in opts:
        return

    await _update_poll(reaction, -1)
    log.info(f'{user} retracted vote for {reaction.emoji} - {poll["prompt"]}')


def setup(bot_: Bot):
    global bot

    bot = bot_

    # settings
    register('poll.createroles', None, lambda _: True, False,
             'Roles allowed to create polls. Defaults to anyone.',
             filter=create_filter)
    register('poll.voteroles', None, lambda _: True, False,
             'Roles allowed to vote in polls. Defaults to anyone.',
             filter=vote_filter)

    # events
    bot.add_listener(on_reaction_add)
    bot.add_listener(on_reaction_remove)

    bot.add_command(poll)


def teardown(bot: Bot):
    global settings

    for key in ('poll.createroles', 'poll.voteroles',):
        del settings[key]
