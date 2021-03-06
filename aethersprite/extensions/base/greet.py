"""
Greet extension; sends a pre-defined greeting to a specified channel when new
users join the guild.
"""

# local
from aethersprite import log
from aethersprite.filters import ChannelFilter
from aethersprite.settings import register, settings
# 3rd party
from discord import Member
from discord.ext.commands import Bot

# filters
channel_filter = ChannelFilter('greet.channel')


async def on_member_join(member: Member):
    "Greet members when they join."

    chan_setting = settings['greet.channel'].get(member)
    msg_setting = settings['greet.message'].get(member)

    if chan_setting is None or msg_setting is None:
        return

    channel = [c for c in member.guild.channels if c.name == chan_setting][0]
    log.info(f'Greeting new member {member} in {member.guild.name} '
             f'#{channel.name}')
    await channel.send(msg_setting.format(name=member.display_name, nl='\n'))


def setup(bot: Bot):
    # settings
    register('greet.channel', None, lambda x: True, False,
             'The channel where greetings should be sent.',
             filter=channel_filter)
    register('greet.message', None, lambda x: True, False,
             'The message new members will be greeted with. You may use '
             'the `{name}` token in your message and it will be replaced '
             'automatically with the member\'s username. The `{nl}` token '
             'will be replaced with a line break (new line).')

    bot.add_listener(on_member_join)
