import typing as t

from tortoise import Tortoise

from unfazed.protocol import DataBaseDriver


class Driver(DataBaseDriver):
    def __init__(self, conf: t.Dict) -> None:
        self._config = conf

    @property
    def config(self) -> t.Dict:
        return self._config

    async def setup(self) -> None:
        await Tortoise.init(config=self.config)
