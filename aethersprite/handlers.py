"""
Event handler utilities

.. note::

    Decorators must be handled differently for methods vs. independent
    functions due to how they are invoked. To decorate a method, assign the
    handler during ``__init__``. An alternative, if you are able to do so,
    is to use a static method. To decorate a plain function, you may use the
    decorator as normal.

    The first argument of the function (not counting ``self`` if the function
    is a method) will be provided with a reference to the bot.

.. code:: python

    from discord.ext.commands import Cog
    from aethersprite.common import handle_ready

    class SomeClass(Cog):
        def __init__(self, bot):
            self.bot = bot
            self.on_ready = handle_ready(self.on_ready)

        def on_ready(self, _):
            # don't care about the bot parameter here, but still have to
            # include it to avoid exceptions
            pass

        @handle_ready
        @staticmethod
        def static_ready(bot)
            # since this is a static method, we need the bot reference to do
            # stuff, as we cannot access "self"
            pass

    @handle_ready
    def on_ready(bot):
        # since we're not a Cog, we need the bot reference to do stuff
        pass
"""

# stdlib
from typing import Callable, Optional


class HandlerCollection:

    "Static collection of handlers; to be inherited from"

    _handlers: Optional[set] = None
    #: The callables in this collection
    handlers: Optional[set] = None

    def __init__(self):
        raise RuntimeError('Singleton collection')

    @classmethod
    def add(cls, handler: Callable) -> None:
        """
        Add handler to collection. This tracks handlers by their `__name__`,
        and is preferred to manipulating `handlers` directly.

        :param handler: The handler callable to hook to the event
        """

        if cls.handlers is None:
            cls.handlers = set([])
            cls._handlers = set([])

        if handler.__name__ in set(cls._handlers):
            return

        cls._handlers.add(handler.__name__)
        cls.handlers.add(handler)


class MemberJoinHandlers(HandlerCollection):

    "on_member_join handlers"


class ReadyHandlers(HandlerCollection):

    "on_ready handlers"


def handle_member_join(f: Callable) -> Callable:
    """
    on_member_join event handler decorator.

    :param f: The handler callable to hook to the event
    :returns: The untouched callable
    """

    MemberJoinHandlers.add(f)

    return f


def handle_ready(f: Callable) -> Callable:
    """
    on_ready event handler decorator.

    :param f: The handler callable to hook to the event
    :returns: The untouched callable
    """

    ReadyHandlers.add(f)

    return f
