# Aethersprite

A [Discord] bot and extension framework.

![Aethersprite](https://github.com/haliphax/aethersprite/raw/assets/aethersprite.jpg)

_This bot is a work in progress. Please excuse my mess..._

## Features

- Multi-server, multi-channel capable
- Built on [discord.py], so new commands are easy to create and integrate
- Server- and channel-specific settings framework for command customization
  - Input and output filters for further customization of settings
- Role-based authorization for commands
- Persistence of data and scheduled events during downtime
- [Flask]-based web application for web hooks, pages, file storage, etc.
- Deal with friendly role and channel names in commands, but store reliable
  IDs for permanence
- [TOML] configuration file for immutable settings
- Able to load multiple commands together as [extension packs]

## Command sets

- `alias`
  Manage aliases for other commands
- `github`
  Information about the project and a link to this repository
- `gmt`
  Get the current time (or an offset from now) in GMT
- `lobotomy`
  A collection of commands for enabling/disabling other commands per-server
  and per-channel
- `nick`
  Change the bot's nickname per-server
- `only`
  Only allow whitelisted commands in a channel
- `poll`
  Create and manage polls that members can vote on
- `roles`
  Allow members to manage their own membership in chosen roles
- `settings`
  A collection of commands for manipulating the bot's settings framework

## Stand-alone settings

Some of the settings in the project do not have corresponding commands, and
operate based entirely on events.

- `greet.channel` _(server)_
  The channel where greeting messages should be sent. Defaults to an empty
  value. Both the channel and message must be set before this feature will be
  enabled.
- `greet.message` _(server)_
  The message that will be used to greet new users when they join the server.
  If set to the default, no greeting will be posted. You may use the `{name}`
  token in your message, and it will be replaced with the new member's
  username. The `{nl}` token will be replaced with a line break (new line).
- `nameonly` _(server)_
  If set to anything other than the default value, the bot will only respond
  if it is mentioned directly
- `nameonly.channel` _(channel)_
  Like `nameonly`, but this setting applies to individual channels
- `prefix` _(server)_
  Change the bot's command prefix (default `!`)

## Extension packs

- [ncfacbot] - The [Nexus Clash] Faction Discord Bot


[discord.py]: https://discordpy.readthedocs.io
[Discord]: https://discordapp.com
[Discord Bot Safe README]: ./ncfacbot/extensions/safe.md
[extension packs]: #extension-packs
[Flask]: https://flask.palletsprojects.com
[ncfacbot]: https://github.com/haliphax/ncfacbot
[Nexus Clash]: https://www.nexusclash.com
[TOML]: https://github.com/toml-lang/toml
