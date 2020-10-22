"""
Greet extension; sends a pre-defined greeting to a specified channel when new
users join the guild.
"""

# 3rd party
from discord import DMChannel, Member
from discord.ext.commands import Context
# local
from .. import log
from ..common import FakeContext, handle_member_join
from ..settings import register, settings


@handle_member_join
async def member_join(member):
    "Greet members when they join."

    ctx = FakeContext(guild={'id': member.guild.id})
    chan_setting = settings['greet.channel'].get(ctx)
    msg_setting = settings['greet.message'].get(ctx)

    if chan_setting is None or msg_setting is None:
        return

    channel = [c for c in member.guild.channels if c.name == chan_setting][0]
    log.info(f'Greeting new member {member} in {member.guild} {channel}')
    await channel.send(msg_setting.format(name=member.display_name))


def setup(bot):
    # settings
    register('greet.channel', 'general', lambda x: True, False,
             'The channel where greetings should be sent.')
    register('greet.message', None, lambda x: True, False,
             'The message new members will be greeted with. You may use '
             'the `{name}` token in your message and it will be replaced '
             'automatically with the member\'s username.')
