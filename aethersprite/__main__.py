"""Entrypoint"""

# stdlib
from asyncio import new_event_loop

# local
from aethersprite import entrypoint

loop = new_event_loop()
loop.run_until_complete(entrypoint())
