"Badnames extension; automatically kick users whose names match a blacklist."

# local
from aethersprite import log
from aethersprite.settings import register, settings
# 3rd party
from discord import Member
from discord.ext.commands import Bot


async def on_member_join(member: Member):
    "Check member names against blacklist on join."

    badnames_setting: str = settings['badnames'].get(member)

    if badnames_setting is None:
        return

    badnames = [n.strip() for n in badnames_setting.split(',')]

    for n in badnames:
        if n in member.name:
            await member.kick(reason='Matched against badnames setting')
            log.warning(f'Kicked {member} due to match against badnames')

            return


def setup(bot: Bot):
    # settings
    register('badnames', None, lambda x: True, False,
             'A list of disallowed substrings to search for in usernames')

    bot.add_listener(on_member_join)
