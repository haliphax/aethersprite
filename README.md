# ncfacbot

A [Nexus Clash] Faction [Discord] bot.

<img src="https://raw.githubusercontent.com/haliphax/ncfacbot/assets/assets/ncfacbot-header.jpg" style="width: 100%; max-width: 100%;" alt="Header image" />

_This bot is a work in progress. Please excuse my mess..._

## Features

- Multi-server, multi-channel capable
- Built on [discord.py], so new commands are easy to create and integrate
- Server- and channel-specific settings framework for command customization
- Role-based authorization for commands
- Persistence of data and scheduled events during downtime

## Commands

- `closest`
  Return the closest tick to the given GMT offset (or now)
- `github`
  Information about the project and a link to this repository
- `gmt`
  Get the current time (or an offset from now) in GMT
- `lobotomy` _(hidden)_
  A collection of commands for enabling/disabling other commands per-server
  and per-channel
- `nick`
  Change the bot's nickname per-server
- `raid`
  A collection of commands for scheduling and announcing raids
- `settings`
  A collection of commands for manipulating the bot's settings framework
- `shop`
  A collection of commands for viewing and maintaining crafting/alchemy/ammo
  shopping lists
- `sm`
  Announce the end of Sorcerers Might, accounting for the countdown tick bug
- `tick`
  GMT timestamp and timespan (e.g. _"8 hour(s), 4 minute(s)"_) of the next tick
  (or _x_ ticks from now)

## Plans

- Set command prefix per-server and per-channel
- Common functions to pull/validate roles and channels from settings
- Split bot framework into separate project, leave NC commands here
- [TOML] configuration file(s) for immutable settings

## Pipe dreams

- Tie-in with TamperMonkey UserScript for aggregating search odds data
- ...


[discord.py]: https://discordpy.readthedocs.io
[Discord]: https://discordapp.com
[Nexus Clash]: https://www.nexusclash.com
[TOML]: https://github.com/toml-lang/toml
