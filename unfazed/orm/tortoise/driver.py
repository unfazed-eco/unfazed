from tortoise import Tortoise
from unfazed.protocol import DataBaseDriver


class Driver(DataBaseDriver):
    def setup(self) -> None:
        Tortoise.init(config=self.config)
