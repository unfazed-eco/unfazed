import asyncio
import typing as t

from tortoise import Tortoise

from unfazed.protocol import DataBaseDriver


class Driver(DataBaseDriver):
    def __init__(self, conf: t.Dict) -> None:
        self._config = conf

    @property
    def config(self) -> t.Dict:
        return self._config

    async def _setup(self) -> None:
        await Tortoise.init(config=self.config)

    def setup(self) -> None:
        # loop = asyncio.get_event_loop()
        # loop.call_soon(self._setup())
        asyncio.ensure_future(self._setup())

