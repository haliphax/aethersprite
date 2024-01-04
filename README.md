# Aethersprite

A [Discord][] bot and extension framework

![Aethersprite](https://github.com/haliphax/aethersprite/raw/assets/aethersprite.jpg)

- [Features](#features)
- [Installing](#installing)
- [Running](#running)
- [Command categories](#command-categories)
- [Independent commands](#independent-commands)
- [Independent settings](#independent-settings)
- [Extension packs](#extension-packs)

## 📣 Features

- Multi-server, multi-channel capable
- Built on [discord.py][], so new commands are easy to create and integrate
- Server- and channel-specific settings framework for command customization
  - Input and output filters for further customization of settings
- Role-based authorization for commands
- Persistence of data and scheduled events during downtime
- [FastAPI][]-based web application for web hooks, pages, file storage, etc.
- Deal with friendly role and channel names in commands, but store reliable IDs
  for permanence
- [TOML][] configuration file for immutable settings
- Able to import external command modules as [extension packs][]

[Back to top](#aethersprite)

## 👷 Installing

First, make a `config.toml` file from the provided `config.example.toml` file,
providing it with your username, API token, and any settings tweaks you wish to
apply.

Then, install the bot package in your Python environment of choice:

```shell
pip install -U 'aethersprite@git+https://github.com/haliphax/aethersprite.git'
```

[Back to top](#aethersprite)

## 🏃 Running

Commands must be run in the same directory as your `config.toml` file.

To start the Discord bot:

```shell
python -m aethersprite
```

To start the web application:

```shell
python -m aethersprite.webapp
```

[Back to top](#aethersprite)

## 📖 Command categories

These categories (referred to as "Cogs") provide multiple commands.

- `alias`
  Manage aliases for other commands
- `only`
  Only allow whitelisted commands in a channel
- `settings`
  Manipulate the bot's settings
- `yeet`
  Disable other commands per-server and per-channel

[Back to top](#aethersprite)

## 🎲 Independent commands

- `github`
  Information about the project and a link to this repository
- `gmt`
  Get the current time (or an offset from now) in GMT
- `nick`
  Change the bot's nickname per-server
- `poll`
  Create and manage polls that members can vote on
- `roles`
  Allow members to manage their own membership in chosen roles
- `roles.catalog`
  Like `roles`, but uses a permanent post rather than on-demand access
- `wipe`
  Wipes all messages in the current channel (after confirmation)

[Back to top](#aethersprite)

## 🔧 Independent settings

Some of the settings in the project do not have corresponding commands, and
operate based entirely on events.

| Setting            | Scope   | Description                                                                                                                                                                                                                                                                                                                                         |
| ------------------ | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `badnames`         | Server  | A comma-separated list of substrings to search for in usernames to auto-kick.                                                                                                                                                                                                                                                                       |
| `greet.channel`    | Server  | The channel where greeting messages should be sent. Defaults to an empty value. Both the channel and message must be set before this feature will be enabled.                                                                                                                                                                                       |
| `greet.message`    | Server  | The message that will be used to greet new users when they join the server. If set to the default, no greeting will be posted. You may use the `{name}` token in your message, and it will be replaced with the new member's username. The `{mention}` token will mention the user. The `{nl}` token will be replaced with a line break (new line). |
| `nameonly`         | Server  | If set to anything other than the default value, the bot will only respond if it is mentioned directly.                                                                                                                                                                                                                                             |
| `nameonly.channel` | Channel | Like `nameonly`, but this setting applies to individual channels.                                                                                                                                                                                                                                                                                   |
| `prefix`           | Server  | Change the bot's command prefix. (Default: `!`) The bot will respond when mentioned directly, regardless of this setting.                                                                                                                                                                                                                           |

[Back to top](#aethersprite)

## 🎁 Extension packs

- [ncfacbot][] - The [Nexus Clash][] Faction Discord Bot
- [Realm TTRPG Bot][]

[Back to top](#aethersprite)

[discord.py]: https://discordpy.readthedocs.io
[discord]: https://discordapp.com
[discord bot safe readme]: ./ncfacbot/extensions/safe.md
[extension packs]: #extension-packs
[fastapi]: https://fastapi.tiangolo.com
[ncfacbot]: https://github.com/haliphax/ncfacbot
[nexus clash]: https://www.nexusclash.com
[realm ttrpg bot]: https://github.com/realm-ttrpg/discord-bot
[toml]: https://github.com/toml-lang/toml
