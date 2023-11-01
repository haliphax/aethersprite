"Aethersprite Discord bot/framework"

# stdlib
from asyncio import new_event_loop
from importlib import import_module
import logging
from os import environ
from os.path import sep
from typing import Optional
from random import seed

# 3rd party
import colorlog
from discord import Activity, ActivityType, DMChannel, Intents, Message
from discord.ext.commands import (
    Bot,
    CheckFailure,
    command,
    CommandNotFound,
    Context,
)
from pretty_help import PrettyHelp
import toml

#: Configuration
config = {
    "bot": {
        "data_folder": ".",
        "extensions": ["aethersprite.extensions.base._all"],
        "help_command": "aehelp",
        "log_level": "INFO",
    },
    "webapp": {
        "proxies": None,
        "flask": {
            "SERVER_NAME": "localhost",
            "SERVER_HOST": "0.0.0.0",
            "SERVER_PORT": 5000,
        },
    },
}

# Load config from file and merge with defaults
config_file = environ.get("AETHERSPRITE_CONFIG", "config.toml")
config = {**config, **toml.load(config_file)}
data_folder = f"{config['bot']['data_folder']}{sep}"

#: Root logger instance
log = logging.getLogger(__name__)
log.setLevel(getattr(logging, config["bot"].get("log_level", "INFO")))
_help = config["bot"].get("help_command", "aehelp")


@command(name=_help, hidden=True)
async def help_proxy(ctx: Context, command: Optional[str] = None):
    if command is None:
        await ctx.send_help()
    else:
        await ctx.send_help(command)


class MyHelp(PrettyHelp):
    def __init__(self):
        super().__init__(delete_invoke=True)

    @property
    def invoked_with(self):
        command_name = _help
        ctx = self.context

        if (
            ctx is None
            or ctx.command is None
            or ctx.command.qualified_name != command_name
        ):
            return command_name

        return ctx.invoked_with


# colored log output
streamHandler = logging.StreamHandler()
streamHandler.setFormatter(
    colorlog.ColoredFormatter(
        "{asctime} {log_color}{levelname:<7}{reset} "
        "{bold_white}{module}:{funcName}{reset} {cyan}\u00bb{reset} {message}",
        style="{",
    )
)
log.addHandler(streamHandler)

#: Activity on login
activity = Activity(name=f"@me {_help}", type=ActivityType.listening)

intents: Intents = Intents.default()
intents.members = True
intents.message_content = True
_helpcmd = MyHelp()


def get_prefixes(bot: Bot, message: Message):
    from .settings import settings

    user_id = bot.user.id
    base = [f"<@!{user_id}> ", f"<@{user_id}> "]
    default = ["!"]

    if "prefix" not in settings:
        return base + default

    prefix = settings["prefix"].get(message)

    if prefix is None:
        return base + default

    return base + [prefix]


#: The bot itself
bot = Bot(command_prefix=get_prefixes, intents=intents, help_command=_helpcmd)


@bot.event
async def on_connect():
    log.info("Connected to Discord")


@bot.event
async def on_disconnect():
    log.info("Disconnected")


@bot.event
async def on_command_error(ctx: Context, error: Exception):
    "Suppress command check failures and invalid commands."

    if isinstance(error, CheckFailure):
        return

    if isinstance(error, CommandNotFound):
        if isinstance(ctx.channel, DMChannel):
            return

        cog = ctx.bot.get_cog("alias")

        if cog is None:
            return

        guild = str(ctx.guild.id)
        aliases = cog.aliases[guild] if guild in cog.aliases else None

        if aliases is None:
            return

        name = ctx.message.content.replace(ctx.prefix, "").split(" ")[0].strip()

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
    log.info(f"Logged in as {bot.user}")
    await bot.change_presence(activity=activity)


@bot.event
async def on_resumed():
    log.info("Connection resumed")


async def entrypoint():
    token = config["bot"].get("token", environ.get("DISCORD_TOKEN", None))
    # need credentials
    assert (
        token is not None
    ), "bot.token not in config and DISCORD_TOKEN not in env variables"
    # for any commands or scheduled tasks, etc. that need random numbers
    seed()
    bot.remove_command("help")
    bot.add_command(help_proxy)

    # load extensions
    for ext in config["bot"]["extensions"]:
        await bot.load_extension(ext)

    if log.level >= logging.DEBUG:
        for key, evs in bot.extra_events.items():
            out = []

            for f in evs:
                out.append(f"{f.__module__}:{f.__name__}")

            log.debug(f"{key} => {out!r}")

    # here we go!
    await bot.start(token)


import_module(".webapp", __name__)
