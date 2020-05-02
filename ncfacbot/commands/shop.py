"Shopping List commands module"

# stdlib
import typing
# 3rd party
from discord import DMChannel
from discord.ext import commands
from sqlitedict import SqliteDict
# local
from .. import bot, log
from ..common import THUMBS_DOWN

#: Hard-coded list of components keyed by lowercase item name for lookup
COMPONENTS = {
    'common': 'Common Component',
    'unc': 'Uncommon Component',
    'rare': 'Rare Component',
    'bag of industrial plastic': 'Bag of Industrial Plastic',
    'batch of leather': 'Batch of Leather',
    'batch of mushrooms': 'Batch of Mushrooms',
    'blood ice': 'Blood Ice',
    'bottle of holy water': 'Bottle of Holy Water',
    'bottle of paradise water': 'Bottle of Paradise Water',
    'bunch of daisies': 'Bunch of Daisies',
    'bunch of lilies': 'Bunch of Lilies',
    'bunch of paradise lilies': 'Bunch of Paradise Lilies',
    'chunk of brass': 'Chunk of Brass',
    'chunk of iron': 'Chunk of Iron',
    'chunk of ivory': 'Chunk of Ivory',
    'chunk of onyx': 'Chunk of Onyx',
    'chunk of steel': 'Chunk of Steel',
    'chunk of stygian iron': 'Chunk of Stygian Iron',
    'femur': 'Femur',
    'gold ingot': 'Gold Ingot',
    'handful of grave dirt': 'Handful of Grave Dirt',
    'humerus': 'Humerus',
    'lead brick': 'Lead Brick',
    'length of chain': 'Length of Chain',
    'length of rope': 'Length of Rope',
    'patch of lichen': 'Patch of Lichen',
    'patch of moss': 'Patch of Moss',
    'piece of stygian coal': 'Piece of Stygian Coal',
    'piece of wood': 'Piece of Wood',
    'rose': 'Rose',
    'silver ingot': 'Silver Ingot',
    'skull': 'Skull',
    'small bottle of gunpowder': 'Small Bottle of Gunpowder',
    'soul ice': 'Soul Ice',
    'spool of copper wire': 'Spool of Copper Wire',
    'sprig of nightshade': 'Sprig of Nightshade',
}


class Shop(commands.Cog, name='shop'):
    """
    Shopping commands

    Used to maintain a personal shopping list of crafting/alchemy ingredients
    """

    _lists = SqliteDict('shop.sqlite3', tablename='shopping_list',
                        autocommit=True)

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='shop.set', brief='Manipulate your shopping list')
    async def set(self, ctx, num, *, item):
        """
        Manipulate your shopping list

        Set your request for [item] to [num], where [num] can be relative. Substring matching is used for [item], so mention any part of its name. If more than one match is returned, you will have to be more specific. At any time if the number of a given item reaches (or dips below) 0, it will be removed from the list.

        The following special item types have been added to the list: Common Components (common), Uncommon Components (unc), and Rare Components (rare).

        Examples:
            !shop.set 5 onyx      (ask for 5 Chunk of Stygian Onyx)
            !shop.set -1 leather  (ask for 1 less Batch of Leather)
            !shop.set +3 unc      (ask for 3 more Uncommon Component)
            !shop.set 0 chain     (clear request for Length of Chain)
        """

        int_num = 0
        name = item.lower()

        try:
            int_num = int(num)
        except ValueError:
            # casting failure
            log.warn(f'{ctx.author} attempted invalid operation: {num} {item}')
            await ctx.message.add_reaction(THUMBS_DOWN)

            return

        log.info(f'{ctx.author} set {item} request to {num}')
        matches = [k for k in COMPONENTS if name in k]
        howmany = len(matches)

        if howmany == 0:
            # no item found
            await ctx.send(':person_shrugging: Not sure what that is supposed '
                           'to be.')

            return

        elif howmany > 1:
            matchstr = '**, **'.join([COMPONENTS[k] for k in matches])
            await ctx.send(f':person_shrugging: Multiple matches: '
                           f' **{matchstr}**. Be more specific.')

            return

        name = COMPONENTS[matches[0]]

        if not ctx.guild.id in self._lists:
            # create new store for guild
            self._lists[ctx.guild.id] = {}

        lists = self._lists[ctx.guild.id]

        if not ctx.author.name in lists:
            # create new list for user
            lists[ctx.author.name] = {}

        items = lists[ctx.author.name]

        if name not in items:
            if int_num <= 0:
                await ctx.send(f':thumbsdown: No **{name}** in your list.')

                return

            items[name] = int_num
        else:
            # either apply an operation or set the value
            if num[0] in ('-', '+'):
                items[name] += int_num
            else:
                items[name] = int_num

        if items[name] <= 0:
            # quantity is less than 1; remove item from list
            await ctx.send(f':red_circle: Removing **{name}** from your list.')
            del items[name]

            if not len(items):
                # last item on the list; remove list from storage
                del lists[ctx.author.name]

            if not len(lists):
                del self._lists[ctx.guild.id]
        else:
            await ctx.send(f':green_circle: Adjusted **{name}**: '
                           f'{items[name]}.')

        if ctx.author.name in lists:
            lists[ctx.author.name] = items

        if ctx.guild.id in self._lists:
            self._lists[ctx.guild.id] = lists

    @commands.command(name='shop.list', brief='Show shopping list(s)')
    async def list(self, ctx, who: typing.Optional[str]):
        """
        Show shopping list(s)

        Show current shopping list for [who]. If no value is provided, your own list will be shown. If "all" is used, a list of users with lists that have at least one item will be shown (but not their items). If "net" is used, a list of all items needed from all combined lists will be shown (but not who needs them).
        """

        if who is None:
            log.info(f'{ctx.author} checked their shopping list')
            who = ctx.author.name
        elif who.lower() == 'all':
            log.info(f'{ctx.author} checked list of names')

            if ctx.guild.id not in self._lists:
                await ctx.send(':person_shrugging: No lists are currently '
                               'stored.')

                return

            liststr = '**, **'.join(self._lists[ctx.guild.id].keys())
            await ctx.send(f':paperclip: Lists: **{liststr}**')

            return

        else:
            log.info(f'{ctx.author} checked shopping list for {who}')

        items = {}

        if who != 'net':
            items = self._lists[ctx.guild.id][who] \
                    if ctx.guild.id in self._lists \
                    and who in self._lists[ctx.guild.id] \
                    else dict()
        elif ctx.guild.id in self._lists:
            ours = self._lists[ctx.guild.id]

            for name in ours.keys():
                lst = ours[name]

                for k in lst.keys():
                    val = lst[k]

                    if k in items:
                        items[k] += val
                    else:
                        items[k] = val

        if not len(items):
            await ctx.send(':person_shrugging: No items to show you.')

            return

        longest = max([len(k) for k in items.keys()])
        first = True
        output = '```'

        for k in items:
            if first:
                first = False
            else:
                output += '\n'

            output += f'{k}{"." * (longest - len(k))}... {items[k]}'

        output += '```'
        await ctx.send(output)

    @commands.command(name='shop.clear')
    async def clear(self, ctx):
        "Empty your shopping list"

        if not ctx.guild.id in self._lists \
                or not ctx.author.name in self._lists[ctx.guild.id]:
            await ctx.send(':person_shrugging: You have no list.')

            return

        lst = self._lists[ctx.guild.id]
        del lst[ctx.author.name]
        self._lists[ctx.guild.id] = lst

        if not len(self._lists[ctx.guild.id]):
            del self._lists[ctx.guild.id]

        await ctx.send(':negative_squared_cross_mark: Your list has been '
                       'cleared.')

bot.add_cog(Shop(bot))
