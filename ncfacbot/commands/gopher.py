"Gopher commands module"

# TODO add list of all known craft/enchant/alchemy items, do partial matching

# stdlib
import typing
# 3rd party
from discord import DMChannel
from discord.ext import commands
from sqlitedict import SqliteDict
# local
from .. import bot, log
from ..common import THUMBS_DOWN


class ShoppingList(object):
    "Class to store in SqliteDict for shopping list"

    def __init__():
        #: Items in the list
        self._items = []


class Gopher(commands.Cog, name='gopher'):
    """
    Gopher commands

    Used to maintain a personal shopping list of crafting/alchemy ingredients
    """

    _lists = SqliteDict('gopher.sqlite3', tablename='shopping_list',
                        autocommit=True)

    def __init__(self, bot):
        self.bot = bot

    def _getitems(self, who):
        "Get list of items for given name (or 'net' for aggregate)"

        if who != 'net':
            return self._lists[who] if who in self._lists else dict()

        items = {}

        for name in self._lists.keys():
            lst = self._lists[name]

            for k in lst.keys():
                val = lst[k]

                if k in items:
                    items[k] += val
                else:
                    items[k] = val

        return items

    @commands.command(name='gopher.set', brief='Manipulate your shopping list')
    async def set(self, ctx, num, *, item):
        """
        Manipulate your shopping list

        Set your request for [item] to [num], where [num] can be relative. Substring matching is used for [item], so mention any part of its name. If more than one match is returned, you will have to be more specific. At any time if the number of a given item reaches (or dips below) 0, it will be removed from the list.

        Examples:
            !gopher.set 5 onyx      (ask for 5 Chunk of Stygian Onyx)
            !gopher.set -1 leather  (ask for 1 less Batch of Leather)
            !gopher.set +3 shade    (ask for 3 more Sprig of Nightshade)
            !gopher.set 0 chain     (clear request for Length of Chain)
        """

        int_num = 0
        name = item

        try:
            int_num = int(num)
        except ValueError:
            # casting failure
            log.warn(f'{ctx.author} attempted invalid operation: {num} {item}')
            await ctx.message.add_reaction(THUMBS_DOWN)

            return

        log.info(f'{ctx.author} set {item} request to {num}')

        if not ctx.author.name in self._lists:
            self._lists[ctx.author.name] = {}

        items = self._lists[ctx.author.name]

        if item not in items:
            if int_num <= 0:
                await ctx.send(f':thumbsdown: No **{name}** in your list.')

                return

            items[item] = int_num
        else:
            # either apply an operation or set the value
            if num[0] in ('-', '+'):
                items[item] += int_num
            else:
                items[item] = int_num

        if items[item] <= 0:
            # quantity is less than 1; remove item from list
            await ctx.send(f':red_circle: Removing **{name}** from your list.')
            del items[item]

            if not len(items):
                # last item on the list; remove list from storage
                del self._lists[ctx.author.name]

                return
        else:
            await ctx.send(f':green_circle: Adjusted **{name}**: {items[item]}.')

        self._lists[ctx.author.name] = items

    @commands.command(name='gopher.list', brief='Show shopping list(s)')
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

            if not len(self._lists):
                await ctx.send(':person_shrugging: No lists are currently '
                               'stored.')

                return

            await ctx.send(':paperclip: Lists: '
                           + ', '.join(self._lists.keys()))

            return

        else:
            log.info(f'{ctx.author} checked shopping list for {who}')

        items = self._getitems(who)

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

            output += f'{k: <{longest}} {items[k]}'

        output += '```'
        await ctx.send(output)

bot.add_cog(Gopher(bot))
