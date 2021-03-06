# stdlib
import logging
from os import environ
from random import seed
from sys import stdout
from typing import Optional
# 3rd party
from discord import Activity, ActivityType, DMChannel, Intents, Message
from discord.ext.commands import (Bot, CheckFailure, command, CommandNotFound,
                                  Context, DefaultHelpCommand,
                                  when_mentioned_or,)
# local
from . import config, log

# logging stuff
streamHandler = logging.StreamHandler(stdout)
streamHandler.setFormatter(logging.Formatter(
    '{asctime} {levelname:<7} <{module}.{funcName}> {message}', style='{'))
log.addHandler(streamHandler)
log.setLevel(getattr(logging, environ.get('LOGLEVEL', 'INFO')))

_help = config['bot']['help_command']

#: Activity on login
activity = Activity(name=f'@mention {_help}', type=ActivityType.listening)


def get_ending_note(self):
    return (f'Type !{_help} <command> for more info on a command.\n'
            f'You can also type !{_help} <category> for more info on a '
            'category.')

DefaultHelpCommand.get_ending_note = get_ending_note


@command(name=_help, hidden=True)
async def aehelp(ctx: Context, command: Optional[str] = None):
    if command is None:
        await ctx.send_help()
    else:
        await ctx.send_help(command)


intents: Intents = Intents.default()
intents.members = True


def get_prefixes(bot: Bot, message: Message):
    from .settings import settings

    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    default = ['!']

    if 'prefix' not in settings:
        return base + default

    prefix = settings['prefix'].get(message)

    if prefix is None:
        return base + default

    return base + [prefix]


#: The bot itself
bot = Bot(command_prefix=get_prefixes, intents=intents)


@bot.event
async def on_connect():
    log.info('Connected to Discord')


@bot.event
async def on_disconnect():
    log.info('Disconnected')


@bot.event
async def on_command_error(ctx: Context, error: Exception):
    "Suppress command check failures and invalid commands."

    if isinstance(error, CheckFailure):
        return

    if isinstance(error, CommandNotFound):
        if isinstance(ctx.channel, DMChannel):
            return

        cog = ctx.bot.get_cog('alias')

        if cog is None:
            return

        guild = str(ctx.guild.id)
        aliases = cog.aliases[guild] if guild in cog.aliases else None

        if aliases is None:
            return

        name = ctx.message.content \
                .replace(ctx.prefix, '').split(' ')[0].strip()

        if name not in aliases:
            return

        cmd = ctx.bot.get_command(aliases[name])

        if cmd is None:
            return

        ctx.command = cmd

        return await ctx.bot.invoke(ctx)

    raise error


@bot.event
async def on_ready():
    "Update presence and fire up registered startup handlers."

    log.info(f'Logged in as {bot.user}')
    await bot.change_presence(activity=activity)


@bot.event
async def on_resumed():
    log.info('Connection resumed')


# redundant, but one last check in case someone wants to get real shifty and
# do something that requires them to import __main__ from another entry point
def entrypoint():
    "aethersprite main entry point."

    token = config['bot'].get('token', environ.get('DISCORD_TOKEN', None))
    # need credentials
    assert token is not None, \
        'bot.token not in config and DISCORD_TOKEN not in env variables'
    # for any commands or scheduled tasks, etc. that need random numbers
    seed()
    bot.remove_command('help')
    bot.add_command(aehelp)

    # load extensions
    for ext in config['bot']['extensions']:
        bot.load_extension(ext)

    if log.level >= logging.DEBUG:
        for key, evs in bot.extra_events.items():
            out = []

            for f in evs:
                out.append(f'{f.__module__}:{f.__name__}')

            log.debug(f'{key} => {out!r}')

    # here we go!
    bot.run(token)

if __name__ == '__main__':
    entrypoint()
