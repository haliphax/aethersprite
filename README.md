# ncfacbot

A [Nexus Clash] Faction [Discord] bot.

<img src="https://raw.githubusercontent.com/haliphax/ncfacbot/assets/assets/ncfacbot-header.jpg" style="width: 100%; max-width: 100%;" alt="Header image" />

_This bot is a work in progress. Please excuse my mess..._

## Features

- Multi-server, multi-channel capable
- Built on [discord.py], so new commands are easy to create and integrate
- Server- and channel-specific settings framework for command customization
- Role-based authorization for commands

## Commands

- `closest`
  Return the closest tick to the given GMT offset (or now)
- `github`
  Information about the project and a link to this repository
- `gmt`
  Get the current time (or an offset from now) in GMT
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
  GMT timestamp and timespan ("8 hours, 4 minutes") of the next tick (or _x_
  ticks from now)


[discord.py]: https://discordpy.readthedocs.io
[Discord]: https://discordapp.com
[Nexus Clash]: https://www.nexusclash.com
