import asyncio

from unfazed.core import Unfazed


def get_asgi_handler():
    unfazed = Unfazed()
    asyncio.run(unfazed.setup())
    return unfazed


application = get_asgi_handler()
